"use client";

import React, { useState } from "react";
import {
  Search,
  Barcode,
  ShoppingCart,
  Trash2,
  Plus,
  Minus,
  CreditCard,
  Banknote,
  Receipt,
  User,
  CheckCircle,
  PauseCircle,
  XCircle,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { formatCurrency } from "@/lib/utils";

interface ProductCatalogItem {
  id: string;
  name: string;
  generic: string;
  barcode: string;
  price: number;
  stock: number;
  isRx: boolean;
}

const mockCatalog: ProductCatalogItem[] = [
  { id: "1", name: "Panadol Extra 500mg (24 Tab)", generic: "Paracetamol", barcode: "628100112233", price: 4.5, stock: 85, isRx: false },
  { id: "2", name: "Augmentin 1g (14 Tab)", generic: "Amoxicillin / Clavulanate", barcode: "628100998877", price: 18.25, stock: 40, isRx: true },
  { id: "3", name: "Brufen 400mg (30 Tab)", generic: "Ibuprofen", barcode: "628100445566", price: 6.75, stock: 120, isRx: false },
  { id: "4", name: "Nexium 40mg (28 Cap)", generic: "Esomeprazole", barcode: "628100778899", price: 28.0, stock: 25, isRx: false },
  { id: "5", name: "Ventolin Inhaler 100mcg", generic: "Salbutamol", barcode: "628100332211", price: 9.5, stock: 60, isRx: true },
];

interface CartLine {
  item: ProductCatalogItem;
  quantity: number;
  discount: number;
}

export default function PosPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [cart, setCart] = useState<CartLine[]>([
    { item: mockCatalog[0], quantity: 2, discount: 0 },
    { item: mockCatalog[2], quantity: 1, discount: 0 },
  ]);
  const [isSuccessModalOpen, setIsSuccessModalOpen] = useState(false);

  const filteredCatalog = mockCatalog.filter(
    (p) =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.generic.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.barcode.includes(searchQuery)
  );

  const addToCart = (product: ProductCatalogItem) => {
    setCart((prev) => {
      const existing = prev.find((line) => line.item.id === product.id);
      if (existing) {
        return prev.map((line) =>
          line.item.id === product.id ? { ...line, quantity: line.quantity + 1 } : line
        );
      }
      return [...prev, { item: product, quantity: 1, discount: 0 }];
    });
  };

  const updateQuantity = (id: string, delta: number) => {
    setCart((prev) =>
      prev
        .map((line) => (line.item.id === id ? { ...line, quantity: line.quantity + delta } : line))
        .filter((line) => line.quantity > 0)
    );
  };

  const removeFromCart = (id: string) => {
    setCart((prev) => prev.filter((line) => line.item.id !== id));
  };

  const subtotal = cart.reduce((acc, line) => acc + line.item.price * line.quantity, 0);
  const tax = subtotal * 0.05; // 5% VAT
  const grandTotal = subtotal + tax;

  const handleCheckout = () => {
    setIsSuccessModalOpen(true);
    setTimeout(() => {
      setIsSuccessModalOpen(false);
      setCart([]);
    }, 2000);
  };

  return (
    <div className="flex flex-col lg:flex-row h-[calc(100vh-8rem)] gap-6 overflow-hidden">
      {/* Left: Product Catalog & Barcode Search */}
      <div className="flex-1 flex flex-col gap-4 overflow-hidden">
        {/* Search Header */}
        <div className="flex items-center gap-3 bg-card p-3 rounded-lg border">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Scan barcode or type medicine name / SKU / active ingredient..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 text-sm"
              autoFocus
            />
          </div>
          <Button variant="outline" className="gap-2 shrink-0">
            <Barcode className="h-4 w-4" /> Scanner Active
          </Button>
        </div>

        {/* Product Grid */}
        <div className="flex-1 overflow-y-auto grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 pr-1">
          {filteredCatalog.map((product) => (
            <Card
              key={product.id}
              onClick={() => addToCart(product)}
              className="cursor-pointer hover:border-primary transition-all flex flex-col justify-between p-4"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <h4 className="font-semibold text-xs leading-snug line-clamp-2">{product.name}</h4>
                  {product.isRx && (
                    <Badge variant="warning" className="text-[10px] px-1 py-0 shrink-0">
                      Rx Only
                    </Badge>
                  )}
                </div>
                <p className="text-[11px] text-muted-foreground mt-1">{product.generic}</p>
              </div>

              <div className="flex items-center justify-between mt-3 pt-2 border-t">
                <span className="text-sm font-bold text-primary">{formatCurrency(product.price)}</span>
                <span className="text-[11px] text-muted-foreground">Stock: {product.stock}</span>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Right: Cart & Checkout Panel */}
      <div className="w-full lg:w-96 flex flex-col bg-card rounded-lg border shadow-sm overflow-hidden shrink-0">
        {/* Cart Header */}
        <div className="p-4 border-b flex items-center justify-between bg-muted/30">
          <div className="flex items-center gap-2">
            <ShoppingCart className="h-4 w-4 text-primary" />
            <span className="font-bold text-sm">Active Cart ({cart.length} items)</span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => setCart([])} className="text-destructive text-xs h-7">
            Clear
          </Button>
        </div>

        {/* Cart Items List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {cart.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-muted-foreground text-xs gap-2">
              <ShoppingCart className="h-8 w-8 text-muted-foreground/40" />
              <span>Cart is empty. Scan barcode or click products to add.</span>
            </div>
          ) : (
            cart.map((line) => (
              <div key={line.item.id} className="flex items-center justify-between p-2.5 rounded-lg border bg-background">
                <div className="flex flex-col flex-1 pr-2">
                  <span className="text-xs font-semibold line-clamp-1">{line.item.name}</span>
                  <span className="text-[10px] text-muted-foreground">
                    {formatCurrency(line.item.price)} × {line.quantity} = {formatCurrency(line.item.price * line.quantity)}
                  </span>
                </div>

                <div className="flex items-center gap-1">
                  <Button variant="outline" size="icon" className="h-6 w-6" onClick={() => updateQuantity(line.item.id, -1)}>
                    <Minus className="h-3 w-3" />
                  </Button>
                  <span className="text-xs font-bold w-5 text-center">{line.quantity}</span>
                  <Button variant="outline" size="icon" className="h-6 w-6" onClick={() => updateQuantity(line.item.id, 1)}>
                    <Plus className="h-3 w-3" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-6 w-6 text-destructive ml-1" onClick={() => removeFromCart(line.item.id)}>
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Totals & Payment Section */}
        <div className="p-4 border-t bg-muted/20 space-y-3">
          <div className="space-y-1.5 text-xs">
            <div className="flex justify-between text-muted-foreground">
              <span>Subtotal</span>
              <span>{formatCurrency(subtotal)}</span>
            </div>
            <div className="flex justify-between text-muted-foreground">
              <span>VAT (5%)</span>
              <span>{formatCurrency(tax)}</span>
            </div>
            <div className="flex justify-between text-sm font-bold pt-1 border-t text-foreground">
              <span>Grand Total</span>
              <span className="text-primary text-base">{formatCurrency(grandTotal)}</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 pt-2">
            <Button onClick={handleCheckout} disabled={cart.length === 0} className="w-full gap-2 bg-emerald-600 hover:bg-emerald-700">
              <Banknote className="h-4 w-4" /> Cash Pay
            </Button>
            <Button onClick={handleCheckout} disabled={cart.length === 0} variant="outline" className="w-full gap-2">
              <CreditCard className="h-4 w-4" /> Card Pay
            </Button>
          </div>
        </div>
      </div>

      {/* Success Notification Modal */}
      {isSuccessModalOpen && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <Card className="max-w-md w-full p-6 text-center space-y-4">
            <CheckCircle className="h-12 w-12 text-emerald-500 mx-auto" />
            <div>
              <h3 className="text-lg font-bold">Transaction Completed!</h3>
              <p className="text-xs text-muted-foreground mt-1">Invoice INV-2026-0992 generated. Stock updated via FEFO.</p>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
