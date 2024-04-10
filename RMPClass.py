import requests
import json
import math

class RateMyProfScraper:
    def __init__(self, schoolid):
        self.UniversityId = schoolid
        self.professorlist = self.createprofessorlist()
        self.indexnumber = False

    def createprofessorlist(self):  # creates List object that includes basic information on all Professors from the IDed University
        tempprofessorlist = []
        num_of_prof = self.GetNumOfProfessors(self.UniversityId)
        num_of_pages = math.ceil(num_of_prof / 20)
        i = 1
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        while i <= num_of_pages:  # the loop inserts all professors into list
            page = requests.get(
                "http://www.ratemyprofessors.com/filter/professor/?&page=" + str(i) +
                "&filter=teacherlastname_sort_s+asc&query=*%3A*&queryoption=TEACHER&queryBy=schoolId&sid=" +
                str(self.UniversityId), headers=headers)
            try:
                temp_jsonpage = json.loads(page.content)
            except json.JSONDecodeError:
                print("Failed to decode JSON from response.")
                return []
            temp_list = temp_jsonpage['professors']
            tempprofessorlist.extend(temp_list)
            i += 1
        return tempprofessorlist

    def GetNumOfProfessors(self, id):  # function returns the number of professors in the university of the given ID.
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        page = requests.get(
            "http://www.ratemyprofessors.com/filter/professor/?&page=1&filter=teacherlastname_sort_s+asc&query=*%3A*&queryoption=TEACHER&queryBy=schoolId&sid=" +
            str(id), headers=headers)
        try:
            temp_jsonpage = json.loads(page.content)
        except json.JSONDecodeError:
            print("Failed to decode JSON from response.")
            return 0
        num_of_prof = temp_jsonpage['remaining'] + 20  # get the number of professors
        return num_of_prof

    def SearchProfessor(self, ProfessorName):
        self.indexnumber = self.GetProfessorIndex(ProfessorName)
        self.PrintProfessorInfo()
        return self.indexnumber

    def GetProfessorIndex(self, ProfessorName):  # function searches for professor in list
        for i in range(len(self.professorlist)):
            if ProfessorName == (self.professorlist[i]['tFname'] + " " + self.professorlist[i]['tLname']):
                return i
        return False  # Return False if not found

    def PrintProfessorInfo(self):  # print search professor's name and RMP score
        if self.indexnumber == False:
            print("Error: Professor not found.")
        else:
            print(self.professorlist[self.indexnumber])

    def PrintProfessorDetail(self, key):  # print search professor's detail
        if self.indexnumber == False:
            print("Error: Professor not found.")
            return "Error"
        else:
            print(self.professorlist[self.indexnumber][key])
            return self.professorlist[self.indexnumber][key]

# Example usage
WilliamPatersonUniversity = RateMyProfScraper(1205)
WilliamPatersonUniversity.SearchProfessor("Cyril Ku")
WilliamPatersonUniversity.PrintProfessorDetail("overall_rating")

MassInstTech = RateMyProfScraper(580)
MassInstTech.SearchProfessor("Robert Berwick")
MassInstTech.PrintProfessorDetail("overall_rating")
