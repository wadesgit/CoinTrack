import winsound
import bitmex
import json
import threading
from datetime import datetime

class Tick():
    def __init__(self, time, price):
        self.time = time
        self.price = price


class PriceChecker():
    # Constructor
    def __init__(self):
        self.levelsList = []                                # Call the @levelsList.setter method and pass it an empty list
        self.currentPrice = 0.0                             # Call the @currentPrice.setter method and pass it 0.0
        self.BitmexClient = bitmex.bitmex(test=False)
        self.previousPrice = 0.0                            # Call the @previousPrice.setter method and pass it 0.0

    @property
    def levelsList(self):
        return self.__levelsList                            # Return the value of __levelsList

    @levelsList.setter
    def levelsList(self, newValue):
        self.__levelsList = newValue                        # Set the value of __levelsList

    @property
    def currentPrice(self):
        return self.__currentPrice                           # Return the value of __currentPrice

    @currentPrice.setter
    def currentPrice(self, newValue):
        self.__currentPrice = newValue                      # Set the value of __currentPrice

    @property
    def previousPrice(self):
        return self.__previousPrice                         # Return the value of __previousPrice

    @previousPrice.setter
    def previousPrice(self, newValue):
        self.__previousPrice = newValue                     # Set the value of __previousPrice

    # Class Methods
    # =============
        

    # Method: Sort and Display the levelsList
    def displayList(self):
        print(chr(27) + "[2J")  # Clear the screen
        print("Price Levels In The List")
        print("========================")
        # Sort the list in reverse order
        self.__levelsList.sort(reverse=True)
        # Print the items in the list (Based on the above sort, numbers should appear from large to small.)
        for level in self.__levelsList:
            level = "${:,.1f}".format(level)
            print(level)
        print("")

    # Display the menu and get user input about what methods to execute next
    @property
    def displayMenu(self):
        min = 0
        max = 5
        errorMsg = "Please enter a valid option between " + str(min) + " and " + str(max)

        print("MENU OPTIONS")
        print("============")
        print("1. Add a price level")
        print("2. Remove a price level")
        print("3. Remove all price levels")
        if (self.__currentPrice > 0):
            print("4. Display the current Bitcoin price here: " + f"${self.__currentPrice:,}")
        else:
            print("4. Display the current Bitcoin price here")
        print("5. Start the monitoring")
        print("0. Exit the program")
        print(" ")

        # Get user input. Keep on requesting input until the user enters a valid number between min and max
        selection = 99
        while selection < min or selection > max:
            try:
                selection = int(input("Please enter one of the options: "))
            except:
                print(errorMsg)  # user did not enter a number
                continue  # skip the following if statement
            if (selection < min or selection > max):
                print(errorMsg)  # user entered a number outside the required range
        return selection  # When this return is finally reached, selection will have a value between (and including) min and max

    # Method: Append a new price level to the levelsList
    def addLevel(self):
        try:
            # Let the user enter a new float value and append it to the list
            Level = float(input("Enter a Price Level to Add: "))
            self.__levelsList.append(Level)
        except:
            # Print and error message if the user entered invalid input
            print("\nPlease enter a Valid Price Level.")

    # Method: Remove an existing price level from the levelsList
    def removeLevel(self):
        try:
            # Let the user enter a new float value. If found in the list, remove it from the list
            Level = float(input("Enter a Price Level to Remove: "))
            self.__levelsList.remove(Level)
        except:
            # Print and error message if the user entered invalid input
            print("\nPlease choose a Price Level that is present in the List")

    # Method: Set levelsList to an empty list
    def removeAllLevels(self):
        # Set levelsList to an empty list
        self.__levelsList.clear()

    # Method: Read levelsList using the data in levelsFile
    def readLevelsFromFile(self):
        try:
            # Set levelsList to an Empty List
            self.__levelsList.clear()
            # Open the File
            with open('levelsFile.json', 'r') as file:
                # Use a loop to read through the file line by line
                for line in file:
                    float(line)
                    # If the last two characters in the line is "\n", remove them
                    line = line.strip('\n')
                    # Append the line to levelsList
                    self.__levelsList.append(float(line))
                # Close the File
                file.close()
        except:
            return

    # Method: Write levelsList to levelsFile (Override the Existing File)
    def writeLevelsToFile(self):
        # Open the file in a way that will override the existing file (if it already exists)
        with open('levelsFile.json', 'w') as file:
            # Use a loop to iterate over levelsList Item by Item
            for level in self.__levelsList:
                # Convert everything in the item to a string then add \n to it - before writing it to the file
                file.write('%s\n' % level)

        # Close the file
        file.close()

    # Function: Display the Bitcoin price in the menu item – to assist the user when setting price levels
    def updateMenuPrice(self):
        # Get the latest Bitcoin info (as a Tick object) from getBitMexPrice(). Name it tickObj.
        tickObj = self.getBitMexPrice()
        # Update the currentPrice property with the Bitcoin price in tickObj.
        self.__currentPrice = tickObj.price

    # Function: Call the Bitmex Exchange
    def getBitMexPrice(self):
        # Send a request to the exchange for Bitcoin's data in $USD ('XBTUSD').
        # The json response is converted into a tuple which we name responseTuple.
        responseTuple = self.BitmexClient.Instrument.Instrument_get(filter=json.dumps({'symbol': 'XBTUSD'})).result()
        # The tuple consists of the Bitcoin information (in the form of a dictionary with key>value pairs) plus
        # some additional meta data received from the exchange.
        # Extract only the dictionary (Bitcoin information) from the tuple.
        responseDictionary = responseTuple[0:1][0][0]
        # Creat a Tick object and set its variables to the timestamp and lastPrice data from the dictionary.
        return Tick(responseDictionary["timestamp"], responseDictionary['lastPrice'])

    # Once this method has been called, it uses a Timer to execute every 2 seconds
    def monitorLevels(self):
        # Create timer to call this method every 2 seconds
        threading.Timer(2.0, self.monitorLevels).start()

        # Since we will obtain the latest current price from the exchange,
        # store the existing value of currentPrice in previousPrice
        self.previousPrice = self.currentPrice

        tickObj = self.getBitMexPrice()
        self.__currentPrice = tickObj.price

        if self.previousPrice == 0.0:
            self.previousPrice = self.currentPrice

        print('')
        print('Price Check at ' + str(datetime.now()) + '   (Press Ctrl+C to stop the monitoring)')
        print('=================================================================================')

        displayList = []

        # Loop through the prices in levelsList.
        # During each loop:
        # - Create a variable called priceLevelLabel consisting of the text 'Price Level:    ' followed
        #   by the price.
        for price in self.levelsList:
            priceLevelLabel = 'Price Level:    ' + str(price)

            # - Add priceLevelLabel and the price as two separate items to a new list (the sub-List).
            priceLevelList = []
            priceLevelList.extend([priceLevelLabel, price])

            # - Append the sub-List to displayList.
            displayList.append(priceLevelList)

        # Create a variable called previousPriceLabel consisting of the text 'Previous Price: ' followed
        # by previousPrice.


        BlueBG = '\033[44m'
        RedBG = '\033[41m'
        GreenBG = '\033[42m'
        NoBG = '\033[0m'

        previousPriceLabel = BlueBG + 'Previous Price: ' + str(self.previousPrice) + NoBG

        # Add previousPriceLabel and previousPrice as two separate items to a new list (the sub-List).
        previousPriceList = []
        previousPriceList.extend([previousPriceLabel, self.previousPrice])

        # Append the sub-List to displayList.
        displayList.append(previousPriceList)

        # SPRINT 5
        # Format the background colour of currentPriceLabel as follows:
        # - If currentPrice > previousPrice: set currentPriceLabel background colour to green
        # - If currentPrice < previousPrice: set currentPriceLabel background colour to red
        # - If currentPrice == previousPrice: set currentPriceLabel background colour to blue

        # Create a variable called currentPriceLabel consisting of the text 'Current Price:  ' followed
        # by currentPrice.

        if self.currentPrice > self.previousPrice:
            currentPriceLabel = GreenBG + 'Current Price:  ' + str(self.currentPrice) + NoBG
        elif self.currentPrice < self.previousPrice:
            currentPriceLabel = RedBG + 'Current Price:  ' + str(self.currentPrice) + NoBG
        elif self.currentPrice == self.previousPrice:
            currentPriceLabel = BlueBG + 'Current Price:  ' + str(self.currentPrice) + NoBG

        # Add currentPriceLabel and currentPrice as two separate items to a new list (the sub-List).
        currentPriceList = []
        currentPriceList.extend([currentPriceLabel, self.currentPrice])

        # Append the sub-List to displayList.
        displayList.append(currentPriceList)

        # Sort displayList using the SECOND item (price) in its sub-lists
        displayList.sort(key=lambda x: x[1], reverse=True)

        # For each sub-List in displayList, print only the label (first item) in the sub-List
        for line in displayList:
            print(line[0])

        # SPRINT 6
        # Loop through displayList
        for i in range(0, len(displayList)):

            # Test if the first item in the current sub-list contains the text "Price Level"
            # Tip: Remember that each sub-list is a list within a list (displayList). So you have
            #       to access its items via displayList followed by TWO indexes.
            line = displayList[i]
            if "Price Level" in line[0]:
                # Extract the second item from the current sub-list into a variable called priceLevel
                priceLevel = line[1]
                # Test if priceLevel is between previousPrice and currentPrice OR
                #         priceLevel == previousPrice OR
                #         priceLevel == currentPrice
                if (
                        (self.previousPrice < priceLevel < self.currentPrice) or (self.previousPrice > priceLevel > self.currentPrice) or (priceLevel == self.previousPrice) or (priceLevel == self.currentPrice)
                ):
                    # Sound the alarm. Pass in the frequency and duration.
                    if self.currentPrice > self.previousPrice:
                        frequency = 800
                        duration = 700
                    else:
                        frequency = 400
                        duration = 700
                    winsound.Beep(frequency, duration)

                    # Print the text 'Alarm' with a green background colour, so that the user
                    # can go back into the historical data to see what prices raised the alarm.
                    print(GreenBG + 'Alarm!' + NoBG)


# *************************************************************************************************
#                                           Main Code Section
# *************************************************************************************************

# Create an object based on the PriceChecker class
checkerObj = PriceChecker()

# Load levelsList from the records in levelsFile
checkerObj.readLevelsFromFile()

# Display the levelsList and Menu; and then get user input for what actions to take
userInput = 99
while userInput != 0:
    checkerObj.displayList()
    userInput = checkerObj.displayMenu
    if (userInput == 1):
        checkerObj.addLevel()
        checkerObj.writeLevelsToFile()  # Write levelsList to LevelsFile
    elif (userInput == 2):
        checkerObj.removeLevel()
        checkerObj.writeLevelsToFile()  # Write levelsList to LevelsFile
    elif (userInput == 3):
        checkerObj.removeAllLevels()
        checkerObj.writeLevelsToFile()  # Write levelsList to LevelsFile
    elif (userInput == 4):
        checkerObj.updateMenuPrice()
    elif (userInput == 5):
        userInput = 0  # Prevent the app from continuing if the user pressed Ctrl+C to stop it
        checkerObj.monitorLevels()