from dataclasses import dataclass


@dataclass
class AnimalClass:
    number_legs: int = None


@dataclass
class MammalClass(AnimalClass):
    pass


@dataclass
class CatClass(MammalClass):
    pet_name: str = None


if __name__ == '__main__':
    x = CatClass(number_legs=4, pet_name='Snowy')
    print(f'{x.pet_name} has {x.number_legs} legs')
