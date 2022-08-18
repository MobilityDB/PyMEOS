class ComparisonError(TypeError):
    def __init__(self, type1, type2) -> None:
        super().__init__(f'Comparison not supported between types {type1} and {type2}')
