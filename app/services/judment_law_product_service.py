from app.repository import JudmentLawProductRepository
class JudmentLawProductSevice:
    def __init__(self,repo:JudmentLawProductRepository):
        self.repo =  repo
    