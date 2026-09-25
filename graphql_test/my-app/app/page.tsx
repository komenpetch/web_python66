"use client";

import { FormEvent, useEffect, useState } from "react";

type Product = {
  id: number;
  name: string;
  price: number;
};

// GraphQL has a single endpoint - every query and mutation is a POST here
const GRAPHQL_URL = "http://127.0.0.1:8000/graphql";

// Strawberry converts snake_case resolvers to camelCase
// (create_product -> createProduct)
const PRODUCTS_QUERY = `
  query {
    products {
      id
      name
      price
    }
  }
`;

const CREATE_PRODUCT_MUTATION = `
  mutation CreateProduct($name: String!, $price: Float!) {
    createProduct(name: $name, price: $price) {
      id
      name
      price
    }
  }
`;

const UPDATE_PRODUCT_MUTATION = `
  mutation UpdateProduct($id: Int!, $name: String!, $price: Float!) {
    updateProduct(id: $id, name: $name, price: $price) {
      id
      name
      price
    }
  }
`;

const DELETE_PRODUCT_MUTATION = `
  mutation DeleteProduct($id: Int!) {
    deleteProduct(id: $id)
  }
`;

// Send a query/mutation and return `data`, throwing on HTTP or GraphQL errors
async function graphqlRequest<T>(
  query: string,
  variables: Record<string, unknown> = {}
): Promise<T> {
  const response = await fetch(GRAPHQL_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, variables }),
  });

  let result;
  try {
    result = await response.json();
  } catch {
    result = null;
  }

  // GraphQL usually returns 200 even on errors, so check `errors` too
  if (result?.errors?.length) {
    throw new Error(result.errors[0].message);
  }

  if (!response.ok || !result) {
    throw new Error(`GraphQL request failed (status ${response.status})`);
  }

  return result.data as T;
}

export default function Home() {
  const [products, setProducts] = useState<Product[]>([]);
  const [name, setName] = useState("");
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

  // QUERY PRODUCTS
  useEffect(() => {
    async function getProducts() {
      try {
        const data = await graphqlRequest<{ products: Product[] }>(PRODUCTS_QUERY);
        setProducts(data.products);
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
    setName("");
    setPrice("");
    setEditingId(null);
  }

  // SELECT PRODUCT FOR EDITING
  function editProduct(product: Product) {
    clearMessages();

    setEditingId(product.id);
    setName(product.name);
    setPrice(String(product.price));
  }

  // CREATE PRODUCT MUTATION
  async function addProduct() {
    const data = await graphqlRequest<{ createProduct: Product }>(
      CREATE_PRODUCT_MUTATION,
      { name: name.trim(), price: Number(price) }
    );

    setProducts((currentProducts) => [...currentProducts, data.createProduct]);

    clearForm();
    showSuccess("Product added successfully");
  }

  // UPDATE PRODUCT MUTATION
  async function updateProduct() {
    if (editingId === null) {
      throw new Error("No product selected for editing");
    }

    const data = await graphqlRequest<{ updateProduct: Product | null }>(
      UPDATE_PRODUCT_MUTATION,
      { id: editingId, name: name.trim(), price: Number(price) }
    );

    const updated = data.updateProduct;
    if (updated === null) {
      throw new Error(`Product with id ${editingId} not found`);
    }

    setProducts((currentProducts) =>
      currentProducts.map((product) =>
        product.id === editingId ? updated : product
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

  // DELETE PRODUCT MUTATION
  async function deleteProduct(productId: number) {
    clearMessages();

    try {
      const data = await graphqlRequest<{ deleteProduct: boolean }>(
        DELETE_PRODUCT_MUTATION,
        { id: productId }
      );

      if (!data.deleteProduct) {
        throw new Error(`Product with id ${productId} not found`);
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
        Product Management (GraphQL)
      </h1>

      <form onSubmit={saveProduct} className="mb-8 space-y-4">
        <h2 className="text-xl font-semibold">
          {editingId === null ? "Add Product" : `Edit Product #${editingId}`}
        </h2>

        <input
          type="text"
          placeholder="Product name"
          value={name}
          onChange={(event) => setName(event.target.value)}
          required
          className="block w-full rounded border p-2"
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

                <p className="text-gray-400">
                  ID: {product.id}
                </p>

                <p className="font-semibold">
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
