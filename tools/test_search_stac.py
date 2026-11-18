import unittest
from datetime import datetime, timezone

from check_stac import CheckError, Provider
from search_stac import (
    is_l2a_collection,
    make_circle_polygon,
    search_provider,
)


PROVIDER = Provider(
    "mock",
    "https://mock.example/stac/v1/",
    "mock.example",
)
NOW = datetime(2026, 11, 18, 9, 0, tzinfo=timezone.utc)


class SearchStacTests(unittest.TestCase):
    def collections(self, _url, _host, _timeout):
        return 200, {
            "collections": [
                {"id": "sentinel-2-l2a", "title": "Sentinel-2 Level-2A"},
                {"id": "sentinel-2-l1c", "title": "Sentinel-2 Level-1C"},
                {"id": "landsat-c2-l2", "title": "Landsat Collection 2 Level-2"},
            ]
        }, 1.0

    def search_fn(self, features=None, links=None):
        payload = {
            "type": "FeatureCollection",
            "features": features if features is not None else [],
            "links": links if links is not None else [],
        }

        def request(_url, _host, _timeout, method, body):
            self.assertEqual(method, "POST")
            self.assertEqual(body["collections"], ["sentinel-2-l2a"])
            self.assertEqual(body["datetime"], "2026-10-19T09:00:00Z/2026-11-18T09:00:00Z")
            self.assertEqual(body["intersects"]["type"], "Polygon")
            return 200, payload, 2.0

        return request

    def test_collection_detection(self):
        self.assertTrue(is_l2a_collection({"id": "sentinel-2-l2a"}))
        self.assertTrue(is_l2a_collection({"title": "Sentinel-2 Level-2A"}))
        self.assertFalse(is_l2a_collection({"id": "sentinel-2-l1c"}))
        self.assertFalse(is_l2a_collection({"id": "landsat-c2-l2"}))

    def test_circle_polygon_is_closed(self):
        polygon = make_circle_polygon()
        ring = polygon["coordinates"][0]
        self.assertEqual(polygon["type"], "Polygon")
        self.assertEqual(ring[0], ring[-1])
        self.assertEqual(len(ring), 65)

    def test_success_reports_safe_item_metadata_only(self):
        feature = {
            "type": "Feature",
            "id": "S2A_TEST_ITEM",
            "collection": "sentinel-2-l2a",
            "properties": {
                "datetime": "2026-11-10T08:00:00Z",
                "eo:cloud_cover": 12.5,
            },
            "assets": {"B02": {"href": "https://assets.example/file.tif?token=secret"}},
        }
        report = search_provider(
            PROVIDER, now=NOW, json_getter=self.collections,
            request_json=self.search_fn([feature]),
        )
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["item_count"], 1)
        self.assertEqual(report["items"][0]["id"], "S2A_TEST_ITEM")
        self.assertEqual(report["items"][0]["cloud_cover"], 12.5)
        self.assertNotIn("assets", str(report))
        self.assertNotIn("secret", str(report))

    def test_empty_search_is_successful(self):
        report = search_provider(
            PROVIDER, now=NOW, json_getter=self.collections,
            request_json=self.search_fn([]),
        )
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["item_count"], 0)

    def test_missing_l2a_collection_fails(self):
        def no_l2a(*_args):
            return 200, {"collections": [{"id": "sentinel-2-l1c"}]}, 1.0

        report = search_provider(PROVIDER, now=NOW, json_getter=no_l2a)
        self.assertEqual(report["error_stage"], "COLLECTION_DISCOVERY")
        self.assertEqual(report["error_class"], "Sentinel2L2ACollectionNotFound")

    def test_invalid_search_schema_fails(self):
        report = search_provider(
            PROVIDER, now=NOW, json_getter=self.collections,
            request_json=lambda *_args: (200, {"features": []}, 1.0),
        )
        self.assertEqual(report["error_stage"], "SEARCH_SCHEMA")


    def test_http_error_is_reported_safely(self):
        def fail(*_args):
            raise CheckError("SEARCH_HTTP", "HTTPError", 503)

        report = search_provider(
            PROVIDER, now=NOW, json_getter=self.collections, request_json=fail,
        )
        self.assertEqual(report["error_stage"], "SEARCH_HTTP")
        self.assertEqual(report["error_http_status"], 503)

    def test_timeout_is_reported_safely(self):
        def fail(*_args):
            raise CheckError("SEARCH_HTTP", "TimeoutError")

        report = search_provider(
            PROVIDER, now=NOW, json_getter=self.collections, request_json=fail,
        )
        self.assertEqual(report["error_class"], "TimeoutError")

    def test_invalid_collections_schema_fails(self):
        report = search_provider(
            PROVIDER, now=NOW,
            json_getter=lambda *_args: (200, {"not_collections": []}, 1.0),
        )
        self.assertEqual(report["error_stage"], "COLLECTIONS_SCHEMA")

    def test_external_next_link_is_blocked(self):
        report = search_provider(
            PROVIDER, now=NOW, json_getter=self.collections,
            request_json=self.search_fn([], [{"rel": "next", "href": "https://evil.example/steal"}]),
        )
        self.assertEqual(report["error_stage"], "PAGINATION")
        self.assertEqual(report["error_class"], "ExternalOrUnsafeLinkBlocked")

    def test_pagination_is_bounded(self):
        calls = []

        def endless_next(_url, _host, _timeout, method, _body):
            calls.append(method)
            return 200, {
                "type": "FeatureCollection",
                "features": [],
                "links": [{"rel": "next", "href": "https://mock.example/stac/v1/search?page=next", "method": "POST", "body": {}}],
            }, 1.0

        report = search_provider(
            PROVIDER, now=NOW, json_getter=self.collections,
            request_json=endless_next,
        )
        self.assertEqual(len(calls), 3)
        self.assertEqual(report["pages_checked"], 3)
        self.assertTrue(report["has_more"])


if __name__ == "__main__":
    unittest.main()
