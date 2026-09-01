"use client";

import { FormEvent, useEffect, useState } from "react";

type Product = {
  id: number;
  name: string;
  description: string;
  price: number;
};

const API_URL = "http://127.0.0.1:8000/products";

export default function Home() {
  const [products, setProducts] = useState<Product[]>([]);
  const [id, setId] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");

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
    const newProduct: Product = {
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

    const updatedProduct: Product = {
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
