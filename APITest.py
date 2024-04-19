import ratemyprofessor

import ratemyprofessor

school = ratemyprofessor.get_school_by_name("Florida International University")
professor = ratemyprofessor.get_professors_by_school_and_name(school, "Richard Whittaker")
if professor is not None:
    print("%sworks in the %s Department of %s." % (professor.name, professor.department, professor.school.name))
    print("Rating: %s / 5.0" % professor.rating)
    print("Difficulty: %s / 5.0" % professor.difficulty)
    print("Total Ratings: %s" % professor.num_ratings)
    if professor.would_take_again is not None:
        print(("Would Take Again: %s" % round(professor.would_take_again, 1)) + '%')
    else:
        print("Would Take Again: N/A")
