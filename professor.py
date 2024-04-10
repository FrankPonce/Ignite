class Professor:
    def __init__(self, ratemyprof_id, first_name, last_name, num_of_ratings, overall_rating, department=None):
        self.ratemyprof_id = ratemyprof_id
        self.name = f"{first_name} {last_name}"
        self.first_name = first_name
        self.last_name = last_name
        self.num_of_ratings = num_of_ratings
        self.overall_rating = 0 if num_of_ratings < 1 else float(overall_rating)
        self.department = department  # Ensure this is correctly set during scraping
        self.reviews = []

    def get_reviews(self):
        return self.reviews

    def add_review(self, review):
        self.reviews.append(review)
