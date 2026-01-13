import unittest
import os
import json
from backend.services.story_detail_fetcher import StoryDetailFetcher

class TestStory57Modals(unittest.TestCase):
    """
    Verification tests for Story 5.7: Story Detail Modals & Reliability Fix
    @story 5.7
    """
    story_id = "5.7"

    def setUp(self):
        # Use the actual project root for verification if possible, 
        # or mock the file system if we just want to test the fetcher
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.fetcher = StoryDetailFetcher(self.project_root)

    def test_fetch_story_details(self):
        # Story 5.7 should exist in our project
        details = self.fetcher.get_story_details("5.7")
        self.assertIsNotNone(details)
        print(f"DEBUG: Story ID: {details.get('story_id')}")
        print(f"DEBUG: Title: {details.get('title')}")
        print(f"DEBUG: Task count: {len(details.get('tasks', []))}")
        print(f"DEBUG: Tasks: {details.get('tasks')}")
        self.assertEqual(details['story_id'], "5.7")
        self.assertTrue(len(details['tasks']) > 0)
        self.assertIn("Acceptance Criteria", details['raw_content'])

    def test_fetch_story_missing(self):
        details = self.fetcher.get_story_details("9.9")
        self.assertIsNone(details)

if __name__ == '__main__':
    unittest.main()
