from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5) # Users wait 1-5 seconds between tasks

    @task
    def get_homepage(self):
        """Simulates a user visiting the homepage."""
        self.client.get("/")

    @task(3) # This task is 3 times more likely to be chosen
    def get_products(self):
        """Simulates a user browsing the products page."""
        self.client.get("/products")

    # You can add more tasks here to simulate more complex user flows
    # e.g., viewing a product, adding to cart, etc.