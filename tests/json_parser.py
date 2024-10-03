import unittest

from src.db_cache import SourceTypes
from src.jsonParser import get_event_objects, GroupEventsKernel


class TestJSONParser(unittest.TestCase):

    def test_gcal_event_kernel(self):
        google_calendars: [GroupEventsKernel] = get_event_objects(
            f"https://raw.githubusercontent.com/AvocadoMoon/Events/refs/heads/main/gcal.json",
            SourceTypes.gCal
        )
        first_group: GroupEventsKernel = google_calendars[0]

        self.assertEqual("New Haven Library", first_group.group_name)
        self.assertEqual(SourceTypes.gCal, first_group.sourceType)
        self.assertEqual("8qf27rmmeun7mat412odluuha11umbhm@import.calendar.google.com", first_group.calendar_ids[0])
        self.assertEqual(22, first_group.event_template.attributedToId)  # group ID
        self.assertEqual("family_education", first_group.event_template.category.name)
        self.assertEqual("93", first_group.event_template.picture.mediaId)


    def test_farmers_event_kernel(self):
        farmers_market: [GroupEventsKernel] = get_event_objects(
            f"https://raw.githubusercontent.com/AvocadoMoon/Events/refs/heads/main/farmers_market.json",
            SourceTypes.json
        )

        first_group: GroupEventsKernel = farmers_market[0]

        self.assertEqual("Stonington",first_group.group_name)
        self.assertEqual(SourceTypes.json, first_group.sourceType)
        self.assertEqual("Stonington Farmers Market", first_group.calendar_ids[0])
        self.assertEqual(25, first_group.event_template.attributedToId) # group ID
        self.assertEqual("food_drink", first_group.event_template.category.name)
        self.assertEqual("96", first_group.event_template.picture.mediaId)

if __name__ == '__main__':
    unittest.main()
