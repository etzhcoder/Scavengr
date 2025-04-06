
const ingredientKey = 'campingIngredients';

export function getIngredients() {
  const stored = localStorage.getItem(ingredientKey);
  return stored ? JSON.parse(stored) : [];
}

export function addIngredient(ingredient) {
  let ingredients = getIngredients();
  ingredient = ingredient.trim();
  if (ingredient && !ingredients.includes(ingredient)) {
    ingredients.push(ingredient);
    localStorage.setItem(ingredientKey, JSON.stringify(ingredients));
  }
}

export function removeIngredient(ingredient) {
  let ingredients = getIngredients();
  ingredients = ingredients.filter(item => item !== ingredient);
  localStorage.setItem(ingredientKey, JSON.stringify(ingredients));
}