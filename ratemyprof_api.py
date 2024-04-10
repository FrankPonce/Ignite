import requests
import json
import math
import csv
import os

from professor import Professor

# This code has been tested using Python 3.6 interpreter and Linux (Ubuntu).
# It should run under Windows, if anything you may need to make some adjustments for the file paths of the CSV files.


class ProfessorNotFound(Exception):
    def __init__(self, search_argument, search_parameter: str = "Name"):

        # What the client is looking for. Ex: "Professor Pattis"
        self.search_argument = self.search_argument

        # The search criteria. Ex: Last Name
        self.search_parameter = search_parameter

    def __str__(self):

        return (
            f"Proessor not found"
            + f" The search argument {self.search_argument} did not"
            + f" match with any professor's {self.search_parameter}"
        )


class RateMyProfApi:
    def __init__(self, school_id: str = "18445", testing: bool = False):
        self.UniversityId = school_id
        # Ensure directory exists
        if not os.path.exists("SchoolID_" + str(self.UniversityId)):
            os.mkdir("SchoolID_" + str(self.UniversityId))
        self.professors = self.scrape_professors(testing)

    def scrape_professors(self, testing: bool = False):
        professors = {}
        num_of_prof = self.get_num_of_professors(self.UniversityId)
        num_of_pages = math.ceil(num_of_prof / 20)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        for i in range(1, num_of_pages + 1):
            page = requests.get(
                f"http://www.ratemyprofessors.com/filter/professor/?&page={i}&filter=teacherlastname_sort_s+asc&query=*%3A*&queryoption=TEACHER&queryBy=schoolId&sid={self.UniversityId}",
                headers=headers
            )
            # Check for a successful request
            if page.status_code == 200:
                json_response = json.loads(page.content)
                for json_professor in json_response["professors"]:
                    professor = Professor(
                        json_professor["tid"],
                        json_professor["tFname"],
                        json_professor["tLname"],
                        json_professor["tNumRatings"],
                        json_professor["overall_rating"]
                    )
                    professors[professor.ratemyprof_id] = professor
            if testing and (i > 1): break
        return professors

    def get_num_of_professors(self, id):
        page = requests.get(
            "http://www.ratemyprofessors.com/filter/professor/?&page=1&filter=teacherlastname_sort_s+asc&query=*%3A*&queryoption=TEACHER&queryBy=schoolId&sid=" + str(
                id))
        print("Status Code:", page.status_code)  # Check the status code
        print("Response Content:", page.content[:500])  # Print first 500 chars of the response

        # Proceed only if the request was successful
        if page.status_code == 200:
            try:
                temp_jsonpage = json.loads(page.content)
                num_of_prof = temp_jsonpage["remaining"] + 20
                return num_of_prof
            except json.JSONDecodeError:
                print("Failed to decode JSON.")
                return 0
        else:
            print("Request failed.")
            return 0

    def search_professor(self, ProfessorName):
        self.indexnumber = self.get_professor_index(ProfessorName)
        self.print_professor_info()
        return self.indexnumber

    def get_professor_by_last_name(self, last_name) -> Professor:
        """
        Return the first professor with the matching last name.
        Case insensitive.
        """
        last_name = last_name.lower()
        for professor_id, professor in self.professors.items():
            if last_name == professor.last_name.lower():
                return professor

        # Raise error if no matching professor found
        raise ProfessorNotFound(last_name, "Last Name")


    def WriteProfessorListToCSV(self):
        csv_columns = [
            "tDept",
            "tSid",
            "institution_name",
            "tFname",
            "tMiddlename",
            "tLname",
            "tid",
            "tNumRatings",
            "rating_class",
            "contentType",
            "categoryType",
            "overall_rating",
        ]
        csv_file = "SchoolID_" + str(self.UniversityId) + ".csv"
        with open(csv_file, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in self.professorlist:
                writer.writerow(data)

    def create_reviews_list(self, tid):
        tempreviewslist = []
        num_of_reviews = self.get_num_of_reviews(tid)
        # RMP only loads 20 reviews per page,
        # so num_of_pages tells us how many pages we need to get all the reviews
        num_of_pages = math.ceil(num_of_reviews / 20)
        i = 1
        while i <= num_of_pages:
            page = requests.get(
                "https://www.ratemyprofessors.com/paginate/professors/ratings?tid="
                + str(tid)
                + "&filter=&courseCode=&page="
                + str(i)
            )
            temp_jsonpage = json.loads(page.content)
            temp_list = temp_jsonpage["ratings"]
            tempreviewslist.extend(temp_list)
            i += 1
        return tempreviewslist

    def get_num_of_reviews(self, id):
        page = requests.get(
            "https://www.ratemyprofessors.com/paginate/professors/ratings?tid="
            + str(id)
            + "&filter=&courseCode=&page=1"
        )
        temp_jsonpage = json.loads(page.content)
        num_of_reviews = temp_jsonpage["remaining"] + 20
        return num_of_reviews

    def WriteReviewsListToCSV(self, rlist, tid):
        csv_columns = [
            "attendance",
            "clarityColor",
            "easyColor",
            "helpColor",
            "helpCount",
            "id",
            "notHelpCount",
            "onlineClass",
            "quality",
            "rClarity",
            "rClass",
            "rComments",
            "rDate",
            "rEasy",
            "rEasyString",
            "rErrorMsg",
            "rHelpful",
            "rInterest",
            "rOverall",
            "rOverallString",
            "rStatus",
            "rTextBookUse",
            "rTimestamp",
            "rWouldTakeAgain",
            "sId",
            "takenForCredit",
            "teacher",
            "teacherGrade",
            "teacherRatingTags",
            "unUsefulGrouping",
            "usefulGrouping",
        ]
        csv_file = (
            "./SchoolID_" + str(self.UniversityId) + "/TeacherID_" + str(tid) + ".csv"
        )
        with open(csv_file, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in rlist:
                writer.writerow(data)

    def get_professors(self, department, preferences):
        # Implement logic to filter professors based on the department and preferences.
        # This is a pseudo-code example:
        matching_professors = []
        for pid, prof in self.professors.items():
            if prof.department == department:  # assuming you've added 'department' to your professor instances
                # Now check preferences like 'Quality > 4' and add to matching_professors if it matches
                if preferences['Quality > 4'] and prof.overall_rating > 4:
                    matching_professors.append(prof)
        return matching_professors

    # Renaming create_reviews_list to get_reviews for consistency
    def get_reviews(self, professor_id):
        # Implement the logic from create_reviews_list here, returning the reviews for the given professor_id
        pass

    def get_departments(self):
        departments = set(prof.department for prof in self.professors.values() if prof.department)
        return list(departments)


# Time for some examples!
if __name__ == '__main__':

    # Getting general professor info!
    uci = RateMyProfApi(1074)


    # uci.search_professor("Pattis")
    # uci.print_professor_detail("overall_rating")
    '''
    MassInstTech = RateMyProfApi(580)
    MassInstTech.search_professor("Robert Berwick")
    MassInstTech.print_professor_detail("overall_rating")

    # Let's try the above class out to get data from a number of schools!
    # William Patterson, Case Western, University of Chicago, CMU, Princeton, Yale, MIT, UTexas at Austin, Duke, Stanford, Rice, Tufts
    # For simple test, try tid 97904 at school 1205
    schools = [1205, 186, 1085, 181, 780, 1222, 580, 1255, 1350, 953, 799, 1040]
    for school in schools:
        print("=== Processing School " + str(school) + " ===")
        rmps = RateMyProfApi(school)
        rmps.WriteProfessorListToCSV()
        professors = rmps.get_professor_list()
        for professor in professors:
            reviewslist = rmps.create_reviews_list(professor.get("tid"))
            rmps.WriteReviewsListToCSV(reviewslist, professor.get("tid"))

    '''
