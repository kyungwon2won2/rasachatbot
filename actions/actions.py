from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import mysql.connector
from mysql.connector import Error

# MySQL 데이터베이스 연결 설정
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='bus_schedule',
            user='root',
            password='1234')
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None

# 예시: 버스 시간표 찾기 액션
class ActionFindBusSchedule(Action):

    def name(self) -> Text:
        return "action_find_bus_schedule"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        location_from = tracker.get_slot('location_from')
        location_to = tracker.get_slot('location_to')
        time = tracker.get_slot('time')
        seat_class = tracker.get_slot('seat_class')

        connection = connect_to_database()
        if connection:
            try:
                cursor = connection.cursor()
                query = ("SELECT * FROM `{}` WHERE location_to = %s AND time = %s AND seat_class = %s").format(location_from)
                cursor.execute(query, (location_to, time, seat_class))
                result = cursor.fetchall()

                if result:
                    surrounding = result[0][3]
                    dispatcher.utter_message(text=f"Bus schedule found: From {location_from} to {location_to} at {time}, {seat_class} class. Surrounding environment: {surrounding}")
                else:
                    dispatcher.utter_message(text="No bus schedule found for the given route and preferences.")

                cursor.close()
            except Error as e:
                dispatcher.utter_message(text="There was an error querying the database.")
                print("SQL query error: ", e)
            finally:
                connection.close()

        return []
    
class ActionCheckScheduleAvailability(Action):
    def name(self) -> Text:
        return "action_check_schedule_availability"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        location_from = tracker.get_slot('location_from')

        connection = connect_to_database()
        if connection:
            try:
                cursor = connection.cursor()
                query = "SELECT COUNT(*) FROM `{}`".format(location_from)
                cursor.execute(query)
                result = cursor.fetchone()

                if result and result[0] > 0:
                    dispatcher.utter_message(text=f"There are available bus schedules from {location_from}.")
                else:
                    dispatcher.utter_message(text=f"There are no available bus schedules from {location_from} currently.")

                cursor.close()
            except Error as e:
                dispatcher.utter_message(text="There was an error querying the database.")
                print("SQL query error: ", e)
            finally:
                connection.close()

        return [] 

# 예시: 목적지 환경에 따른 추천 액션
class ActionRecommendDestinationEnvironment(Action):
    def name(self) -> Text:
        return "action_recommend_destination_environment"    

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        location_from = tracker.get_slot('location_from')
        surrounding_preference = tracker.get_slot('surrounding')

        connection = connect_to_database()
        if connection:
            try:
                cursor = connection.cursor()
                query = "SELECT DISTINCT location_to FROM `{}` WHERE surrounding = %s".format(location_from)
                cursor.execute(query, (surrounding_preference,))
                result = cursor.fetchall()

                if result:
                    location_tos = ', '.join([row[0] for row in result])
                    dispatcher.utter_message(text=f"Based on your surrounding preference, recommended location_tos from {location_from} are: {location_tos}")
                else:
                    dispatcher.utter_message(text=f"No location_tos from {location_from} match your surrounding preference.")

                cursor.close()
            except Error as e:
                dispatcher.utter_message(text="There was an error querying the database.")
                print("SQL query error: ", e)
            finally:
                connection.close()

        return []


# 예시: 목적지 제안 액션
class ActionSuggestDestination(Action):
    # (이전과 동일한 name 메서드)
    def name(self) -> Text:
        return "action_suggest_destination"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        location_from = tracker.get_slot('location_from')

        connection = connect_to_database()
        if connection:
            try:
                cursor = connection.cursor()
                query = "SELECT DISTINCT location_to FROM `{}`".format(location_from)
                cursor.execute(query)
                result = cursor.fetchall()

                if result:
                    location_tos = ', '.join([row[0] for row in result])
                    dispatcher.utter_message(text=f"Suggested location_tos from {location_from} are: {location_tos}")
                else:
                    dispatcher.utter_message(text=f"There are no location_tos available from {location_from}.")

                cursor.close()
            except Error as e:
                dispatcher.utter_message(text="There was an error querying the database.")
                print("SQL query error: ", e)
            finally:
                connection.close()

        return []

# 예시: 목적지 일정 표시 액션
class ActionShowlocation_toSchedule(Action):
    # (이전과 동일한 name 메서드)
    def name(self) -> Text:
        return "action_show_location_to_schedule"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        location_from = tracker.get_slot('location_from')
        location_to = tracker.get_slot('location_to')

        connection = connect_to_database()
        if connection:
            try:
                cursor = connection.cursor()
                query = "SELECT time, seat_class, surrounding FROM `{}` WHERE location_to = %s".format(location_from)
                cursor.execute(query, (location_to,))
                result = cursor.fetchall()

                if result:
                    schedules = '\n'.join([f"At {row[0]}, {row[1]} class, Surrounding: {row[2]}" for row in result])
                    dispatcher.utter_message(text=f"Available schedules from {location_from} to {location_to}:\n{schedules}")
                else:
                    dispatcher.utter_message(text=f"No schedules found from {location_from} to {location_to}.")

                cursor.close()
            except Error as e:
                dispatcher.utter_message(text="There was an error querying the database.")
                print("SQL query error: ", e)
            finally:
                connection.close()

        return []