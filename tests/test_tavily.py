from crewai_tools import TavilySearchTool
from crewai_tools import SerperDevTool

# # Test TavilySearchTool with advanced search depth
# search_tool = TavilySearchTool(search_depth='advanced')
# print("Search Results:")
# print(search_tool.run(query="2 bedroom apartments in ikeja lagos for rent with a budget of 3000000 yearly"))




# Initialize the tool
tool = SerperDevTool()

# Run a simple search
print(tool.run(search_query="2 bedroom apartments in ikeja lagos for rent with a budget of less than 4,000,000 naira yearly"))


# # Test TavilyExtractorTool with include_images=True
# extract_tool = TavilyExtractorTool(include_images=True)
# print("\nExtraction Results:")
# print(extract_tool.run(urls="https://nigeriapropertycentre.com/for-rent/flats-apartments/lagos/ikeja/ogba/3184646-lovely-2-bedroom-flat"))