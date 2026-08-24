"""
ImageNet plant/vegetation class mapping for Stage A validation.

Maps ImageNet-1K class NAMES to plant-related categories.
Indices are resolved at runtime from torchvision model metadata
to avoid hardcoding potentially version-dependent index values.
"""

# ImageNet-1K class names that correspond to plants, leaves,
# flowers, fruits, vegetables, and vegetation.
# Source: ILSVRC 2012 synset labels (torchvision standard ordering)
PLANT_RELATED_CLASS_NAMES = {
    # ── Fruits ──────────────────────────────────────────────
    "Granny Smith",
    "banana",
    "strawberry",
    "orange",
    "lemon",
    "fig",
    "pineapple",
    "jackfruit",
    "custard apple",
    "pomegranate",

    # ── Vegetables & Squash ─────────────────────────────────
    "acorn squash",
    "butternut squash",
    "spaghetti squash",
    "zucchini",
    "cucumber",
    "artichoke",
    "bell pepper",
    "broccoli",
    "cauliflower",
    "head cabbage",
    "cardoon",

    # ── Flowers ─────────────────────────────────────────────
    "daisy",
    "yellow lady's slipper",
    "rapeseed",

    # ── Mushrooms (plant-adjacent, accept as organic) ──────
    "agaric",
    "hen-of-the-woods",
    "bolete",
    "ear",
    "coral fungus",
    "stinkhorn",
    "earthstar",

    # ── Grains & Seeds ──────────────────────────────────────
    "corn",
    "ear",           # ear of corn in some label sets
    "hip",           # rose hip
    "acorn",

    # ── Plant containers & plant-associated ─────────────────
    "pot",           # flower pot (often shows plant)
    "vase",          # often has flowers
}

# Additional keywords for fuzzy matching against ImageNet class names.
# If an ImageNet class name CONTAINS any of these substrings (case-insensitive),
# it is considered plant-related. This catches variants and compound names.
PLANT_KEYWORD_FRAGMENTS = [
    "flower",
    "plant",
    "leaf",
    "tree",
    "bush",
    "herb",
    "vine",
    "grass",
    "seed",
    "fruit",
    "vegetable",
    "blossom",
    "petal",
    "fern",
    "moss",
    "cactus",
    "palm",
    "willow",
    "oak",
    "pine",
    "maple",
    "orchid",
    "tulip",
    "rose",
    "lily",
    "sunflower",
    "poppy",
    "clover",
    "wheat",
    "rice",
    "barley",
    "sorghum",
    "millet",
    "cotton",
    "tobacco",
    "hay",
    "straw",
    "mushroom",
    "fungus",
    "lichen",
    "algae",
]


def build_plant_class_indices(imagenet_categories: list) -> set:
    """
    Given the ordered list of ImageNet-1K category names from torchvision,
    returns the set of integer indices that correspond to plant-related classes.

    Args:
        imagenet_categories: List of 1000 class name strings from
            torchvision model weights metadata.

    Returns:
        Set of integer indices (0-999) for plant-related classes.
    """
    plant_indices = set()

    for idx, class_name in enumerate(imagenet_categories):
        name_lower = class_name.lower().strip()

        # Exact match against curated set
        if class_name in PLANT_RELATED_CLASS_NAMES:
            plant_indices.add(idx)
            continue

        # Case-insensitive exact match
        if name_lower in {n.lower() for n in PLANT_RELATED_CLASS_NAMES}:
            plant_indices.add(idx)
            continue

        # Substring / keyword fragment match
        for fragment in PLANT_KEYWORD_FRAGMENTS:
            if fragment.lower() in name_lower:
                plant_indices.add(idx)
                break

    return plant_indices
