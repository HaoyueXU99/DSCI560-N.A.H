'''
responses.py

The file contains two Python functions for generating markdown-formatted responses about travel options. 
- get_cheapest_flights_response, sorts a dataset of flight information by price and generates a response listing the top cheapest flights, including details like airline and timing. 
- get_hotels_response, selects top hotels from a dataset based on price and reviews for a specified city and stay duration, and formats a response detailing hotel names, prices, locations, and ratings. 

Both functions include a URL for booking and are designed to provide quick, informative travel summaries.
'''

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
    # Get the top num_hotels hotels.
    hotels = hotels.head(num_hotels)
    response = f"Here are the top {num_hotels} hotels for your {night}-night stay in {city} (based on price and reviews):\n\n"

    for idx, row in hotels.iterrows():
        response += f"#### :hotel: #{idx + 1} {row['name']}\n\n"
        response += f"- **Price**: ${row['price']} per night\n"
        response += f"- **Location**: {row['location']}\n"
        response += f"- **Rating**: {row['rating']}/10\n\n"



    response += f"[Book Your Stay]({url})\n"
    
    return response