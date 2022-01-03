import math

class Point:
    """
    Represents a point in two-dimensional geometric coordinates

    >>> p0 = Point()
    >>> p1 = Point(3, 4)
    >>> p0.calculate_distance(p1)
    5.0
    """
    def __init__(self, x: float = 0, y: float = 0) -> None:
        """
        Initilize the position of a new point. The x and y
        coordinates can be specified. If thay are not, the
        point defaults to the origin
        """
        self.move(x, y)

    def move(self, x: float, y: float) -> None:
        """
        Move the point to a new location in 2D space

        :param x: float x-coordinate
        :param y: float y-coordinate
        """
        self.x = x
        self.y = y

    def reset(self) -> None:
        """
        Reset the point back ro the gemetrix origin: 0, 0
        """
        self.move(0,0)

    def calculate_distance(self, other: "Point") -> float:
        """
        Calculate the Euclidean distance from this point
        to a second point passed as parameter

        :param other: Point instance
        :return: float distance
        """
        return math.hypot(self.x - other.x, self.y - other.y)


p0 = Point()
print(p0.x, p0.y)

p1 = Point(3, 4)
print(p1.x, p1.y)

print(p0.calculate_distance(p1))

