from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()


class PlannerQueryViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('ai_app:planner-query')
        self.valid_payload = {
            "prompt": "Summarize key steps for planning a weekend trip.",
            "use_search": True
        }

    @patch('ai_app.services.generate_planner_response')
    def test_successful_query(self, mock_generate):
        # Mock the service response
        mock_generate.return_value = (
            "Start by choosing a destination.",
            [{'uri': 'http://example.com/source', 'title': 'Travel Planning Guide'}]
        )

        response = self.client.post(self.url, self.valid_payload, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['response_text'], "Start by choosing a destination.")
        self.assertTrue(mock_generate.called)

    def test_unauthenticated_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, 403)  # Forbidden

# Add tests for MoodDetectionView and service layer if needed.
