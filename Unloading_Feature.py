import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Container dimensions
W, H = 200, 100

class Rectangle:
    def __init__(self, width, height, id, group):
        self.original_width = width
        self.original_height = height
        self.width = width
        self.height = height
        self.id = id
        self.group = group  # A, B, C
        self.x = None
        self.y = None
        self.placed = False
        self.rotated = False

    def rotate(self):
        self.width, self.height = self.height, self.width
        self.rotated = not self.rotated

    def area(self):
        return self.width * self.height

def generate_rectangles_by_type(loads):
    rectangles_by_type = []       #This is a list containing three lists or each group
    idx = 1
    for load in reversed(loads):  # Reverse for FILO (First In Last Out)
        group_rects = []          #group_rects contain rectangles of one type. First iteration group C and then last iteration group A
        prefix = load.get('prefix')
        for i in range(load['count']):
            rect = Rectangle(load['width'], load['height'], f"{prefix}{idx}", group=prefix)
            group_rects.append(rect)
            idx += 1
        group_rects.sort(key=lambda r: r.area(), reverse=True)   #Sort each group by area. Needed for Bottom-left first heuristic
        rectangles_by_type.append(group_rects)
    return rectangles_by_type  # [[C], [B], [A]]

def does_overlap(new_rect, placed_rects, x, y):      #Overlapping logic is the same
    for rect in placed_rects:
        if (x < rect.x + rect.width and x + new_rect.width > rect.x and
            y < rect.y + rect.height and y + new_rect.height > rect.y):
            return True
    return False

#The logic is to allocate a zone for each group w.r.t the total area of each group
def zone_based_placement(rectangles_by_type):
    placed = []

    #Compute area per group
    type_areas = [sum(r.area() for r in group) for group in rectangles_by_type]
    total_area = sum(type_areas)

    #Compute proportional widths
    zone_widths = [W * (a / total_area) for a in type_areas]

    #Get zone start x positions
    zone_starts = [0]
    for width in zone_widths[:-1]:
        zone_starts.append(zone_starts[-1] + width)

    #Place each group within its zone
    for idx, group in enumerate(rectangles_by_type):
        x_start = zone_starts[idx]
        x_end = x_start + zone_widths[idx]
        candidate_positions = [(x_start, 0)]

        #The rectangles in each group are placed in the respective zones using the same Bottom-left first heuristic
        for rect in group:
            placed_flag = False
            for cx, cy in sorted(candidate_positions, key=lambda p: (p[1], p[0])):
                for rotate in [False, True]:
                    if rotate:
                        rect.rotate()

                    if (cx + rect.width <= x_end and cy + rect.height <= H and
                        not does_overlap(rect, placed, cx, cy)):
                        rect.x, rect.y = cx, cy
                        rect.placed = True
                        placed.append(rect)
                        candidate_positions.append((cx + rect.width, cy))
                        candidate_positions.append((cx, cy + rect.height))
                        placed_flag = True
                        break
                    if rotate:
                        rect.rotate()
                if placed_flag:
                    break
    return placed

def visualize_packing(rectangles):
    fig, ax = plt.subplots()
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_title("Delivery-Aware Rectangle Packing")

    # Define color per type
    colors = {'A': 'tomato', 'B': 'gold', 'C': 'lightgreen'}
    borders = {'A': 'darkred', 'B': 'orange', 'C': 'green'}

    for rect in rectangles:
        if rect.placed:
            patch = patches.Rectangle(
                (rect.x, rect.y), rect.width, rect.height,
                linewidth=1, edgecolor=borders.get(rect.group, 'black'),
                facecolor=colors.get(rect.group, 'gray')
            )
            ax.add_patch(patch)
            label = rect.id + (" (R)" if rect.rotated else "")
            ax.text(rect.x + 2, rect.y + 2, label, fontsize=6)
    ax.set_aspect('equal')
    plt.grid(True)
    plt.show()

def calculate_wasted_area(rectangles):
    used_area = sum(rect.area() for rect in rectangles if rect.placed)
    total_area = W * H
    return total_area - used_area

if __name__ == "__main__":
    random.seed(42)

    loads = [
        {'width': 30, 'height': 20, 'count': 20, 'prefix': 'A'},
        {'width': 15, 'height': 25, 'count': 20, 'prefix': 'B'},
        {'width': 20, 'height': 10, 'count': 20, 'prefix': 'C'},
    ]

    #Generate and group rectangles
    rectangles_by_type = generate_rectangles_by_type(loads)

    #Place rectangles using zone logic
    placed_rectangles = zone_based_placement(rectangles_by_type)

    #Visualize 
    visualize_packing(placed_rectangles)
    wasted = calculate_wasted_area(placed_rectangles)
    print("Total wasted area:", wasted)
