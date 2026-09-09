"use client";

import { FormEvent, useEffect, useState } from "react";

type Category = {
  id: number;
  name: string;
};

type Product = {
  id: number;
  name: string;
  description: string;
  price: number;
  categories: Category[];
};

const API_URL = "http://127.0.0.1:8000/products";
const CATEGORIES_API_URL = "http://127.0.0.1:8000/categories";

export default function Home() {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [id, setId] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [categoryName, setCategoryName] = useState("");
  const [editingCategoryId, setEditingCategoryId] = useState<number | null>(null);
  const [categoryEditName, setCategoryEditName] = useState("");

  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);

  function clearMessages() {
    setSuccessMessage("");
    setErrorMessage("");
  }

  function showError(message: string) {
    setErrorMessage(message);
    setSuccessMessage("");
  }

  function showSuccess(message: string) {
    setSuccessMessage(message);
    setErrorMessage("");
  }

  // Safely parse a JSON response body without throwing on empty/invalid bodies
  async function parseJsonSafe(response: Response) {
    try {
      return await response.json();
    } catch {
      return null;
    }
  }

  // GET PRODUCTS
  useEffect(() => {
    async function getProducts() {
      try {
        const response = await fetch(API_URL);
        const result = await parseJsonSafe(response);

        if (!response.ok) {
          throw new Error(
            result?.detail || `Failed to fetch products (status ${response.status})`
          );
        }

        setProducts(result ?? []);
      } catch (error) {
        console.error(error);

        if (error instanceof Error) {
          showError(error.message);
        } else {
          showError("Failed to fetch products");
        }
      } finally {
        setLoading(false);
      }
    }

    getProducts();
  }, []);

  // GET CATEGORIES
  useEffect(() => {
    async function getCategories() {
      try {
        const response = await fetch(CATEGORIES_API_URL);
        const result = await parseJsonSafe(response);

        if (!response.ok) {
          throw new Error(
            result?.detail || `Failed to fetch categories (status ${response.status})`
          );
        }

        setCategories(result ?? []);
      } catch (error) {
        console.error(error);
      }
    }

    getCategories();
  }, []);

  // CLEAR FORM
  function clearForm() {
    setId("");
    setName("");
    setDescription("");
    setPrice("");
    setEditingId(null);
  }

  // SELECT PRODUCT FOR EDITING
  function editProduct(product: Product) {
    clearMessages();

    setEditingId(product.id);
    setId(String(product.id));
    setName(product.name);
    setDescription(product.description);
    setPrice(String(product.price));
  }

  // POST PRODUCT
  async function addProduct() {
    const newProduct = {
      id: Number(id),
      name: name.trim(),
      description: description.trim(),
      price: Number(price),
    };

    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(newProduct),
    });

    const result = await parseJsonSafe(response);

    if (!response.ok) {
      throw new Error(
        result?.detail || `Failed to add product (status ${response.status})`
      );
    }

    setProducts((currentProducts) => [...currentProducts, result]);

    clearForm();
    showSuccess("Product added successfully");
  }

  // PUT PRODUCT
  async function updateProduct() {
    if (editingId === null) {
      throw new Error("No product selected for editing");
    }

    const updatedProduct = {
      id: editingId,
      name: name.trim(),
      description: description.trim(),
      price: Number(price),
    };

    const response = await fetch(`${API_URL}/${editingId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(updatedProduct),
    });

    const result = await parseJsonSafe(response);

    if (!response.ok) {
      throw new Error(
        result?.detail || `Failed to update product (status ${response.status})`
      );
    }

    setProducts((currentProducts) =>
      currentProducts.map((product) =>
        product.id === editingId ? result : product
      )
    );

    clearForm();
    showSuccess("Product updated successfully");
  }

// SUBMIT FORM
  async function saveProduct(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearMessages();

    try {
      if (editingId === null) {
        await addProduct();
      } else {
        await updateProduct();
      }
    } catch (error) {
      if (error instanceof Error) {
        showError(error.message);
      } else {
        showError("Failed to save product");
      }
    }
  }

  // DELETE PRODUCT
  async function deleteProduct(productId: number) {
    clearMessages();

    try {
      const response = await fetch(`${API_URL}/${productId}`, {
        method: "DELETE",
      });

      const result = await parseJsonSafe(response);

      if (!response.ok) {
        throw new Error(
          result?.detail || `Failed to delete product (status ${response.status})`
        );
      }

      setProducts((currentProducts) =>
        currentProducts.filter((product) => product.id !== productId)
      );

      if (editingId === productId) {
        clearForm();
      }

      showSuccess(`Product with id ${productId} deleted successfully`);
    } catch (error) {
      console.error(error);

      if (error instanceof Error) {
        showError(error.message);
      } else {
        showError("Failed to delete product");
      }
    }
  }

  // SELECT CATEGORY FOR EDITING
  function editCategory(category: Category) {
    clearMessages();
    setEditingCategoryId(category.id);
    setCategoryEditName(category.name);
  }

  // CANCEL CATEGORY EDIT
  function cancelCategoryEdit() {
    setEditingCategoryId(null);
    setCategoryEditName("");
  }

  // ADD OR UPDATE CATEGORY
  async function saveCategory(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearMessages();

    const isEditing = editingCategoryId !== null;
    const name = (isEditing ? categoryEditName : categoryName).trim();

    try {
      const response = await fetch(
        isEditing ? `${CATEGORIES_API_URL}/${editingCategoryId}` : CATEGORIES_API_URL,
        {
          method: isEditing ? "PUT" : "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ name }),
        }
      );

      const result = await parseJsonSafe(response);

      if (!response.ok) {
        throw new Error(
          result?.detail ||
            `Failed to ${isEditing ? "update" : "add"} category (status ${response.status})`
        );
      }

      if (isEditing) {
        setCategories((currentCategories) =>
          currentCategories.map((category) =>
            category.id === editingCategoryId ? result : category
          )
        );
        setProducts((currentProducts) =>
          currentProducts.map((product) => ({
            ...product,
            categories: product.categories.map((category) =>
              category.id === editingCategoryId ? result : category
            ),
          }))
        );
        cancelCategoryEdit();
        showSuccess("Category updated successfully");
      } else {
        setCategories((currentCategories) => [...currentCategories, result]);
        setCategoryName("");
        showSuccess("Category added successfully");
      }
    } catch (error) {
      if (error instanceof Error) {
        showError(error.message);
      } else {
        showError(`Failed to ${isEditing ? "update" : "add"} category`);
      }
    }
  }

  // DELETE CATEGORY
  async function deleteCategory(categoryId: number) {
    clearMessages();

    try {
      const response = await fetch(`${CATEGORIES_API_URL}/${categoryId}`, {
        method: "DELETE",
      });

      const result = await parseJsonSafe(response);

      if (!response.ok) {
        throw new Error(
          result?.detail || `Failed to delete category (status ${response.status})`
        );
      }

      setCategories((currentCategories) =>
        currentCategories.filter((category) => category.id !== categoryId)
      );
      setProducts((currentProducts) =>
        currentProducts.map((product) => ({
          ...product,
          categories: product.categories.filter(
            (category) => category.id !== categoryId
          ),
        }))
      );

      if (editingCategoryId === categoryId) {
        cancelCategoryEdit();
      }

      showSuccess("Category deleted successfully");
    } catch (error) {
      if (error instanceof Error) {
        showError(error.message);
      } else {
        showError("Failed to delete category");
      }
    }
  }

  // LINK CATEGORY TO PRODUCT
  async function linkCategory(productId: number, category: Category) {
    clearMessages();

    try {
      const response = await fetch(
        `${API_URL}/${productId}/categories/${category.id}`,
        { method: "POST" }
      );

      const result = await parseJsonSafe(response);

      if (!response.ok) {
        throw new Error(
          result?.detail || `Failed to add category (status ${response.status})`
        );
      }

      setProducts((currentProducts) =>
        currentProducts.map((product) =>
          product.id === productId
            ? { ...product, categories: [...product.categories, category] }
            : product
        )
      );

      showSuccess("Category added to product");
    } catch (error) {
      if (error instanceof Error) {
        showError(error.message);
      } else {
        showError("Failed to add category to product");
      }
    }
  }

  // UNLINK CATEGORY FROM PRODUCT
  async function unlinkCategory(productId: number, categoryId: number) {
    clearMessages();

    try {
      const response = await fetch(
        `${API_URL}/${productId}/categories/${categoryId}`,
        { method: "DELETE" }
      );

      const result = await parseJsonSafe(response);

      if (!response.ok) {
        throw new Error(
          result?.detail || `Failed to remove category (status ${response.status})`
        );
      }

      setProducts((currentProducts) =>
        currentProducts.map((product) =>
          product.id === productId
            ? {
                ...product,
                categories: product.categories.filter(
                  (category) => category.id !== categoryId
                ),
              }
            : product
        )
      );

      showSuccess("Category removed from product");
    } catch (error) {
      if (error instanceof Error) {
        showError(error.message);
      } else {
        showError("Failed to remove category from product");
      }
    }
  }

  return (
    <main className="mx-auto max-w-3xl p-8">
      <h1 className="mb-6 text-3xl font-bold">
        Product Management
      </h1>

      <form onSubmit={saveProduct} className="mb-8 space-y-4">
        <h2 className="text-xl font-semibold">
          {editingId === null ? "Add Product" : "Edit Product"}
        </h2>

        <input
          type="number"
          placeholder="Product ID"
          value={id}
          onChange={(event) => setId(event.target.value)}
          required
          readOnly={editingId !== null}
          className="block w-full rounded border p-2 disabled:bg-gray-200"
        />

        <input
          type="text"
          placeholder="Product name"
          value={name}
          onChange={(event) => setName(event.target.value)}
          required
          className="block w-full rounded border p-2"
        />

        <textarea
          placeholder="Product description"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          required
          className="block w-full rounded border border-gray-500 bg-gray-900 p-2 text-white placeholder-gray-400"
        />

        <input
          type="number"
          step="0.01"
          placeholder="Product price"
          value={price}
          onChange={(event) => setPrice(event.target.value)}
          required
          className="block w-full rounded border p-2"
        />

        <button
          type="submit"
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          {editingId === null ? "Add Product" : "Update Product"}
        </button>

        {editingId !== null && (
          <button
            type="button"
            onClick={clearForm}
            className="ml-2 rounded bg-gray-500 px-4 py-2 text-white hover:bg-gray-600"
          >
            Cancel
          </button>
        )}
      </form>

      <form onSubmit={saveCategory} className="mb-4 flex gap-2">
        <input
          type="text"
          placeholder={editingCategoryId === null ? "New category name" : "Category name"}
          value={editingCategoryId === null ? categoryName : categoryEditName}
          onChange={(event) =>
            editingCategoryId === null
              ? setCategoryName(event.target.value)
              : setCategoryEditName(event.target.value)
          }
          required
          className="flex-1 rounded border p-2"
        />

        <button
          type="submit"
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          {editingCategoryId === null ? "Add Category" : "Save Category"}
        </button>

        {editingCategoryId !== null && (
          <button
            type="button"
            onClick={cancelCategoryEdit}
            className="rounded bg-gray-500 px-4 py-2 text-white hover:bg-gray-600"
          >
            Cancel
          </button>
        )}
      </form>

      {categories.length > 0 && (
        <ul className="mb-8 space-y-1">
          {categories.map((category) => (
            <li
              key={category.id}
              className="flex items-center justify-between rounded border px-3 py-1 text-sm"
            >
              <span>{category.name}</span>
              <span className="flex gap-1">
                <button
                  type="button"
                  onClick={() => editCategory(category)}
                  className="rounded bg-yellow-500 px-2 py-0.5 text-white hover:bg-yellow-600"
                >
                  Edit
                </button>
                <button
                  type="button"
                  onClick={() => deleteCategory(category.id)}
                  className="rounded bg-red-600 px-2 py-0.5 text-white hover:bg-red-700"
                >
                  Delete
                </button>
              </span>
            </li>
          ))}
        </ul>
      )}

      {successMessage && (
        <p className="mb-4 text-green-600">
          {successMessage}
        </p>
      )}

      {errorMessage && (
        <p className="mb-4 text-red-600">
          {errorMessage}
        </p>
      )}

      <h2 className="mb-3 text-xl font-semibold">
        Products
      </h2>

      {loading ? (
        <p>Loading products...</p>
      ) : products.length === 0 ? (
        <p>No products found.</p>
      ) : (
        <ul className="space-y-4">
          {products.map((product) => (
            <li key={product.id} className="rounded border p-4">
              <div className="mb-3">
                <h3 className="text-lg font-semibold">
                  {product.name}
                </h3>

                <p className="text-gray-300">
                  ID: {product.id}
                </p>

                <p className="text-gray-100">
                  {product.description}
                </p>

                <p className="font-semibold text-white">
                  Price: $
                  {product.price.toLocaleString("en-US", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </p>

                <div className="text-gray-300">
                  Categories:{" "}
                  {(product.categories ?? []).length === 0 ? (
                    "None"
                  ) : (
                    <span className="inline-flex flex-wrap gap-1 align-middle">
                      {(product.categories ?? []).map((category) => (
                        <span
                          key={category.id}
                          className="inline-flex items-center gap-1 rounded bg-gray-700 px-2 py-0.5 text-white"
                        >
                          {category.name}
                          <button
                            type="button"
                            onClick={() => unlinkCategory(product.id, category.id)}
                            className="text-red-300 hover:text-red-100"
                            aria-label={`Remove ${category.name} from ${product.name}`}
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </span>
                  )}
                </div>

                <select
                  key={(product.categories ?? []).length}
                  defaultValue=""
                  onChange={(event) => {
                    const category = categories.find(
                      (item) => String(item.id) === event.target.value
                    );
                    if (category) linkCategory(product.id, category);
                  }}
                  className="mt-2 rounded border bg-white p-1 text-sm text-gray-900"
                >
                  <option value="" disabled>
                    Add category...
                  </option>
                  {categories
                    .filter(
                      (category) =>
                        !(product.categories ?? []).some((item) => item.id === category.id)
                    )
                    .map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                </select>
              </div>

              <button
                type="button"
                onClick={() => editProduct(product)}
                className="mr-2 rounded bg-yellow-500 px-3 py-1 text-white hover:bg-yellow-600"
              >
                Edit
              </button>

              <button
                type="button"
                onClick={() => deleteProduct(product.id)}
                className="rounded bg-red-600 px-3 py-1 text-white hover:bg-red-700"
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
