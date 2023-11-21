# responses.py


# #Generate a text response for the cheapest flights.
# def get_cheapest_flights_response(flight_data, url, num_flights=5):
#     # Sort the DataFrame by the 'Price' column in ascending order to get the cheapest flights.
#     cheapest_flights = flight_data.sort_values(by='price').head(num_flights)

#     # Generate a text response based on the cheapest flights.
#     response = f"Here are the top {num_flights} cheapest flights from {flight_data['origin'][0].upper()} to {flight_data['destination'][0].upper()}:\n"
    
#     for idx, row in cheapest_flights.iterrows():
#         response += f"{idx + 1}. For {row['price']}, departure airline {row['departure_airline']}, departure time {row['deptime_o']}, arrival time {row['arrtime_d']}. Return airline {row['return_airline']}, departure time {row['deptime_d']}, arrival time  {row['arrtime_o']}\n"
    
#     response += f"\nTo book your flight, visit {url}"
    
#     return response



# #Generate a text response for hotels.
# def get_hotels_response(hotels, city, night, url, num_hotels=5):
#     hotels = hotels.head(num_hotels)
#     response = f"Here are the top {num_hotels} hotels (based on price and review) for your {night}-night stay in {city}:\n"
#     i = 1
#     for idx, row in hotels.iterrows():
#         response += f"{i}. For ${row['price']}, stay in '{row['name']}'. It's located in {row['location']} and has a rating of {row['rating']}\n"
#         i+=1
#     response += f"\nTo book your stay, visit {url}"
    
#     return response



# Generate a text response for the cheapest flights.
def get_cheapest_flights_response(flight_data, url, num_flights=5):
    # Sort the DataFrame by the 'Price' column in ascending order to get the cheapest flights.
    cheapest_flights = flight_data.sort_values(by='price').head(num_flights)

    # Generate a text response based on the cheapest flights.
    response = f"Here are the top {num_flights} cheapest flights from {flight_data['origin'][0].upper()} to {flight_data['destination'][0].upper()}:\n\n"
    
    for idx, row in cheapest_flights.iterrows():
        response += f"#### :airplane: #{idx + 1} Price: {row['price']}\n\n"
        response += f"- **Departure Airline**: {row['departure_airline']}, **Time**: {row['deptime_o']} → {row['arrtime_d']}\n"
        response += f"- **Return Airline**: {row['return_airline']}, **Time**: {row['deptime_d']} → {row['arrtime_o']}\n\n"
    response += f"[Book Your Flight]({url})\n"
    
    return response

# Generate a text response for hotels.
def get_hotels_response(hotels, city, night, url, num_hotels=5):
    hotels = hotels.head(num_hotels)
    response = f"Here are the top {num_hotels} hotels for your {night}-night stay in {city} (based on price and reviews):\n\n"

    for idx, row in hotels.iterrows():
        response += f"#### :hotel: #{idx + 1} {row['name']}\n\n"
        response += f"- **Price**: ${row['price']} per night\n"
        response += f"- **Location**: {row['location']}\n"
        response += f"- **Rating**: {row['rating']}/10\n\n"



    response += f"[Book Your Stay]({url})\n"
    
    return response