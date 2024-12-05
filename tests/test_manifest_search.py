import unittest
from app import app
from database import db_session, init_db
from generator.output.models import Manifest, Client, Vessel, Voyage, Port, User
from datetime import datetime

class TestManifestSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.client = app.test_client()
        init_db()
        
        # Create test data
        shipper = Client(name="Test Shipper Corp")
        consignee = Client(name="Test Consignee Ltd")
        vessel = Vessel(name="Test Vessel")
        voyage = Voyage(voyage_number="V123")
        user = User(username="testuser", email="testuser@example.com")  # Added email
        
        db_session.add_all([shipper, consignee, vessel, voyage, user])
        db_session.commit()
        
        # Create test manifests
        manifests = [
            Manifest(
                bill_of_lading="BOL123",
                shipper_id=shipper.id,
                consignee_id=consignee.id,
                vessel_id=vessel.id,
                voyage_id=voyage.id,
                manifester_id=user.id,
                date_of_receipt=datetime.now()
            ),
            Manifest(
                bill_of_lading="BOL456",
                shipper_id=shipper.id,
                consignee_id=consignee.id,
                vessel_id=vessel.id,
                voyage_id=voyage.id,
                manifester_id=user.id,
                date_of_receipt=datetime.now()
            )
        ]
        db_session.add_all(manifests)
        db_session.commit()
        
        cls.test_data = {
            'shipper': shipper,
            'consignee': consignee,
            'vessel': vessel,
            'voyage': voyage,
            'user': user,
            'manifests': manifests
        }

    def test_search_by_bill_of_lading(self):
        """Test searching by bill of lading number"""
        response = self.client.get('/manifest/search?query=BOL123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BOL123', response.data)
        self.assertNotIn(b'BOL456', response.data)

    def test_search_by_shipper_name(self):
        """Test searching by shipper name"""
        response = self.client.get('/manifest/search?query=Shipper Corp')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BOL123', response.data)
        self.assertIn(b'BOL456', response.data)  # Both manifests should appear as they share the shipper

    def test_search_by_vessel_name(self):
        """Test searching by vessel name"""
        response = self.client.get('/manifest/search?query=Test Vessel')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BOL123', response.data)
        self.assertIn(b'BOL456', response.data)

    def test_search_by_voyage_number(self):
        """Test searching by voyage number"""
        response = self.client.get('/manifest/search?query=V123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BOL123', response.data)
        self.assertIn(b'BOL456', response.data)

    def test_case_insensitive_search(self):
        """Test that search is case insensitive"""
        response = self.client.get('/manifest/search?query=test vessel')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BOL123', response.data)
        self.assertIn(b'BOL456', response.data)

    def test_partial_match_search(self):
        """Test that search works with partial matches"""
        response = self.client.get('/manifest/search?query=123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BOL123', response.data)
        self.assertNotIn(b'BOL456', response.data)

    def test_empty_search(self):
        """Test that empty search returns all results"""
        response = self.client.get('/manifest/search?query=')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BOL123', response.data)
        self.assertIn(b'BOL456', response.data)

    def test_no_results_search(self):
        """Test search with no matching results"""
        response = self.client.get('/manifest/search?query=nonexistent')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'BOL123', response.data)
        self.assertNotIn(b'BOL456', response.data)

    @classmethod
    def tearDownClass(cls):
        # Clean up test data
        db_session.query(Manifest).delete()
        db_session.query(Client).delete()
        db_session.query(Vessel).delete()
        db_session.query(Voyage).delete()
        db_session.query(User).delete()
        db_session.commit()

if __name__ == '__main__':
    unittest.main()
