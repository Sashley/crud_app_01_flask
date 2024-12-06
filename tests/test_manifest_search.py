import unittest
from app import app
from database import db_session, init_db
from generator.output.models.manifest import Manifest
from generator.output.models.client import Client
from generator.output.models.vessel import Vessel
from generator.output.models.voyage import Voyage
from generator.output.models.port import Port
from generator.output.models.user import User
from datetime import datetime

class TestManifestSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        cls.client = app.test_client()
        init_db()
        
        # Create test data
        shipper1 = Client(name="Test Shipper Corp")
        shipper2 = Client(name="Another Shipper")
        vessel1 = Vessel(name="Test Vessel")
        vessel2 = Vessel(name="Another Vessel")
        voyage1 = Voyage(name="V123")
        voyage2 = Voyage(name="V456")
        user = User(name="testuser", email="testuser@example.com")
        
        db_session.add_all([shipper1, shipper2, vessel1, vessel2, voyage1, voyage2, user])
        db_session.commit()
        
        # Create test manifests with different relationships
        manifests = [
            Manifest(
                bill_of_lading="BOL123",
                shipper_id=shipper1.id,
                consignee_id=shipper2.id,
                vessel_id=vessel1.id,
                voyage_id=voyage1.id,
                manifester_id=user.id,
                date_of_receipt=datetime.now()
            ),
            Manifest(
                bill_of_lading="BOL456",
                shipper_id=shipper2.id,
                consignee_id=shipper1.id,
                vessel_id=vessel2.id,
                voyage_id=voyage2.id,
                manifester_id=user.id,
                date_of_receipt=datetime.now()
            )
        ]
        db_session.add_all(manifests)
        db_session.commit()
        
        cls.test_data = {
            'shipper1': shipper1,
            'shipper2': shipper2,
            'vessel1': vessel1,
            'vessel2': vessel2,
            'voyage1': voyage1,
            'voyage2': voyage2,
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
        response = self.client.get('/manifest/search?query=Test Shipper Corp')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BOL123', response.data)
        self.assertNotIn(b'BOL456', response.data)

    def test_search_by_vessel_name(self):
        """Test searching by vessel name"""
        response = self.client.get('/manifest/search?query=Test Vessel')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BOL123', response.data)
        self.assertNotIn(b'BOL456', response.data)

    def test_search_by_voyage_name(self):
        """Test searching by voyage name"""
        response = self.client.get('/manifest/search?query=V123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BOL123', response.data)
        self.assertNotIn(b'BOL456', response.data)

    def test_case_insensitive_search(self):
        """Test that search is case insensitive"""
        response = self.client.get('/manifest/search?query=test vessel')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'BOL123', response.data)
        self.assertNotIn(b'BOL456', response.data)

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
