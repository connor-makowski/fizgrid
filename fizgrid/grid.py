import type_enforced

@type_enforced.Enforcer
class Grid:
    def __init__(self, name:str, x_size:int, y_size:int, density:int=1):
        self.name = name
        self.x_size = x_size
        self.y_size = y_size
        self.density = density
        self.cells = [[[] for _ in range(x_size*density)] for _ in range(y_size*density)]
        self.agents = {}

    def __repr__(self):
        return f"Grid({self.name} {self.x_size}x{self.y_size})"
    
    def get_cell(self, x:int, y:int):
        try:
            return self.cells[int(y*self.density)][int(x*self.density)]
        except:
            raise ValueError(f"Position ({x},{y}) is out of bounds.")
        



    



    