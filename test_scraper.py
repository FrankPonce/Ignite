from ratemyprof_api import RateMyProfApi

# Replace 'your_university_id' with the actual ID for Florida International University
university_id = '18445'
rate_my_prof_api = RateMyProfApi(school_id=university_id)

# Call the scraping method to test
rate_my_prof_api.scrape_professors()

# Test getting departments
departments = rate_my_prof_api.get_departments()
print("Departments:", departments)

# If you have implemented get_professors in RateMyProfApi
# (The following line assumes that you have such a method)
professors = rate_my_prof_api.get_professors('Computer Science', preferences={})
print("Professors in Computer Science:", professors)
