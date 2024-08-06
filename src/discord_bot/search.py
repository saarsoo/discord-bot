import difflib


def search(
    search_strs: list[str], source_strs: list[str]
) -> dict[str, list[str]]:
    result_groups = {recipe: [] for recipe in search_strs}

    for search_recipe in search_strs:
        matches = []

        available_recipe_names = [r.lower() for r in source_strs]
        if search_recipe in available_recipe_names:
            matches = [
                r for r in source_strs if search_recipe.lower() == r.lower()
            ]
        else:
            matches = difflib.get_close_matches(
                search_recipe.lower(), available_recipe_names
            )
            matches = [
                r for r in source_strs if search_recipe.lower() in r.lower()
            ]

        if not matches:
            matches = [
                r for r in source_strs if search_recipe.lower() in r.lower()
            ]

        if matches:
            better_matches = [
                match for match in matches if search_recipe.lower() in match.lower()
            ]
            if better_matches:
                matches = better_matches

            if len(matches) == 1 or matches[0].lower() == search_recipe.lower():
                matched_recipe = matches[0]
                result_groups[search_recipe].append(matched_recipe)
            else:
                result_groups[search_recipe].extend(matches)

    return result_groups