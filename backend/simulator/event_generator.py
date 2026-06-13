"""
Event Simulator — Fires diverse mock security events for demo.
Each event uses different users, locations, and attack types.
"""
import random
import time

# FIX #3: Diverse events with different users, locations, and attack types
EVENTS = [
    {
        # Event 1: swastik.kumar — impossible travel from Romania
        "type": "login",
        "user": "swastik.kumar",
        "timestamp": "2026-06-14T02:17:00Z",
        "details": {
            "location": "Romania",
            "device_id": "DESKTOP-ROM-01",
            "ip": "185.220.101.45",
            "normal_location": "Mumbai, IN",
            "device_known": False
        }
    },
    {
        # Event 2: anita.sharma (CFO) — unusual access to finance DB
        "type": "login",
        "user": "anita.sharma",
        "timestamp": "2026-06-14T03:42:00Z",
        "details": {
            "location": "Singapore",
            "device_id": "LAPTOP-FIN-02",
            "ip": "103.45.67.89",
            "normal_location": "Mumbai, IN",
            "device_known": False
        }
    },
    {
        # Event 3: john.doe (intern) — unauthorized database access
        "type": "access",
        "user": "john.doe",
        "timestamp": "2026-06-14T11:23:00Z",
        "details": {
            "target": "db_finance",
            "target_type": "DATABASE",
            "action": "SELECT * FROM payroll_records",
            "privilege": "intern",
            "normal_access": False
        }
    },
    {
        # Event 4: swarnim.patel — large data exfiltration
        "type": "data_transfer",
        "user": "swarnim.patel",
        "timestamp": "2026-06-14T14:31:00Z",
        "details": {
            "source": "db_customer",
            "target_type": "DATABASE",
            "destination": "s3://external-bucket",
            "bytes_transferred": 45000000,
            "normal_pattern": False
        }
    }
]

# Dynamic event generator for varied demos
LOCATIONS = ["Romania", "Singapore", "Brazil", "China", "Russia", "Nigeria"]
DEVICES = ["DESKTOP-UNK-01", "LAPTOP-NEW-02", "PHONE-UNK-03", "TABLET-UNK-04"]
USERS = ["swastik.kumar", "anita.sharma", "john.doe", "rakshit.singh", "michael.ross"]

def generate_random_event() -> dict:
    """Generate a random event for testing variability."""
    return {
        "type": random.choice(["login", "access", "data_transfer"]),
        "user": random.choice(USERS),
        "timestamp": f"2026-06-14T{random.randint(0,23):02d}:{random.randint(0,59):02d}:00Z",
        "details": {
            "location": random.choice(LOCATIONS),
            "device_id": random.choice(DEVICES),
            "ip": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
            "normal_location": "Mumbai, IN",
            "device_known": random.choice([True, False]),
        }
    }

def get_demo_events() -> list:
    """Return the 4 curated demo events."""
    return EVENTS

def simulate_event(event: dict = None) -> dict:
    """Fire a single event. If none provided, generate a random one."""
    if event is None:
        return generate_random_event()
    return event
