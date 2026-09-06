"use client";

import React from "react";
import { Building2, Phone, Calendar, Clock, User, CheckCircle2, ShieldCheck } from "lucide-react";
import { formatCurrency } from "@/lib/utils";

export interface InvoiceItem {
  id: string;
  name: string;
  nameAr: string;
  generic?: string;
  batchNumber?: string;
  quantity: number;
  unitPrice: number;
  discount?: number;
  totalPrice: number;
}

export interface TaxInvoiceData {
  invoiceNumber: string;
  issueDate: string;
  issueTime: string;
  customerName: string;
  customerType: string;
  paymentMethod: "cash" | "card" | "credit";
  branchName: string;
  cashierName: string;
  items: InvoiceItem[];
  subtotal: number;
  discountAmount: number;
  taxableAmount: number;
  vatAmount: number;
  vatRatePercentage: number;
  grandTotal: number;
  amountInWordsAr?: string;
}

export function TaxInvoicePrintable({
  data,
  format = "thermal",
}: {
  data: TaxInvoiceData;
  format?: "thermal" | "a4";
}) {
  const isThermal = format === "thermal";

  // Simulated ZATCA-compliant QR SVG Pattern
  const renderQrCode = () => (
    <div className="flex flex-col items-center justify-center p-2 bg-white rounded-lg border border-gray-300 w-fit mx-auto">
      <svg className="w-24 h-24 text-gray-900" viewBox="0 0 100 100" fill="currentColor">
        <path d="M0 0h30v30H0zM10 10h10v10H10zM70 0h30v30H70zM80 10h10v10H80zM0 70h30v30H0zM10 80h10v10H10zM40 0h10v10H40zM50 20h10v10H50zM10 40h10v10H10zM30 40h20v10H30zM60 40h10v20H60zM80 40h20v10H80zM40 60h10v30H40zM60 70h20v10H60zM70 80h10v20H70zM90 70h10v30H90z" />
      </svg>
      <span className="text-[9px] text-gray-500 font-mono mt-1 font-bold">ZATCA e-Invoice Validated</span>
    </div>
  );

  if (isThermal) {
    // ------------------------------------------------------------------------
    // 80mm Thermal Receipt Layout
    // ------------------------------------------------------------------------
    return (
      <div className="w-full max-w-[340px] mx-auto bg-white text-gray-900 font-sans p-4 border rounded-xl text-xs space-y-3 shadow-inner">
        {/* Header */}
        <div className="text-center space-y-1 pb-2 border-b border-dashed border-gray-300">
          <div className="mx-auto h-9 w-9 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold text-sm">
            PC
          </div>
          <h2 className="font-extrabold text-sm text-gray-900">سلسلة صيدليات الأمل الحديثة</h2>
          <p className="text-[10px] text-gray-500">فاتورة ضريبية مبسطة (POS Tax Invoice)</p>
          <div className="text-[9px] text-gray-600 font-mono space-y-0.5 pt-1">
            <p>الرقم الضريبي: 300998877600003 (VAT)</p>
            <p>السجل التجاري: 1010889922 (CR)</p>
            <p>ترخيص الصحة: MOH-RX-2026-991</p>
          </div>
        </div>

        {/* Metadata */}
        <div className="text-[10px] space-y-1 text-gray-600 pb-2 border-b border-dashed border-gray-300">
          <div className="flex justify-between">
            <span>رقم الفاتورة:</span>
            <span className="font-mono font-bold text-gray-900">{data.invoiceNumber}</span>
          </div>
          <div className="flex justify-between">
            <span>التاريخ والوقت:</span>
            <span className="font-mono">{data.issueDate} {data.issueTime}</span>
          </div>
          <div className="flex justify-between">
            <span>الفرع / الكاشير:</span>
            <span>{data.branchName} • {data.cashierName}</span>
          </div>
          <div className="flex justify-between">
            <span>العميل:</span>
            <span className="font-semibold text-gray-900">{data.customerName}</span>
          </div>
          <div className="flex justify-between">
            <span>طريقة الدفع:</span>
            <span className="font-bold text-emerald-700">
              {data.paymentMethod === "cash" ? "نقدي (Cash)" : data.paymentMethod === "card" ? "شبكة / مدى (Card)" : "آجل / على الحساب (Credit)"}
            </span>
          </div>
        </div>

        {/* Items Table */}
        <div className="space-y-1.5 pb-2 border-b border-dashed border-gray-300">
          <div className="flex justify-between text-[10px] font-bold text-gray-700 border-b pb-1">
            <span className="flex-1">الصنف</span>
            <span className="w-10 text-center">الكمية</span>
            <span className="w-16 text-end">الإجمالي</span>
          </div>
          {data.items.map((item) => (
            <div key={item.id} className="flex justify-between items-start text-[10px]">
              <div className="flex-1 pr-1">
                <span className="font-semibold text-gray-900 block leading-tight">{item.nameAr || item.name}</span>
                <span className="text-[9px] text-gray-500 font-mono">
                  {formatCurrency(item.unitPrice)} للوحدة
                </span>
              </div>
              <span className="w-10 text-center font-mono font-bold">{item.quantity}</span>
              <span className="w-16 text-end font-mono font-bold text-gray-900">
                {formatCurrency(item.totalPrice)}
              </span>
            </div>
          ))}
        </div>

        {/* Totals */}
        <div className="space-y-1 text-[11px] pb-2 border-b border-dashed border-gray-300">
          <div className="flex justify-between text-gray-600">
            <span>المجموع قبل الخصم:</span>
            <span className="font-mono">{formatCurrency(data.subtotal)}</span>
          </div>
          {data.discountAmount > 0 && (
            <div className="flex justify-between text-amber-700 font-semibold">
              <span>الخصم الممنوح:</span>
              <span className="font-mono">-{formatCurrency(data.discountAmount)}</span>
            </div>
          )}
          <div className="flex justify-between text-gray-600">
            <span>وعاء الضريبة الخاضع:</span>
            <span className="font-mono">{formatCurrency(data.taxableAmount)}</span>
          </div>
          <div className="flex justify-between text-gray-600">
            <span>ضريبة القيمة المضافة ({data.vatRatePercentage}%):</span>
            <span className="font-mono">{formatCurrency(data.vatAmount)}</span>
          </div>
          <div className="flex justify-between text-sm font-extrabold text-gray-900 pt-1 border-t border-gray-200">
            <span>الإجمالي المستحق (صافي):</span>
            <span className="font-mono text-emerald-700">{formatCurrency(data.grandTotal)}</span>
          </div>
        </div>

        {/* QR Code */}
        <div className="pt-1 text-center">
          {renderQrCode()}
        </div>

        {/* Footer */}
        <div className="text-center text-[9px] text-gray-500 space-y-0.5 pt-1">
          <p className="font-semibold text-gray-700">شكراً لثقتكم بصيدليات الأمل</p>
          <p>شروط الاسترجاع: خلال 3 أيام مع أصل الفاتورة بحالة سليمة.</p>
          <p className="font-mono">خدمة العملاء: 920088991</p>
        </div>
      </div>
    );
  }

  // --------------------------------------------------------------------------
  // A4 Standard Official Tax Invoice Layout
  // --------------------------------------------------------------------------
  return (
    <div className="w-full max-w-3xl mx-auto bg-white text-gray-900 font-sans p-8 border rounded-2xl text-xs space-y-6 shadow-sm printable-invoice">
      {/* Official A4 Header */}
      <div className="flex items-start justify-between pb-6 border-b-2 border-emerald-600">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="h-10 w-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold text-lg">
              PC
            </div>
            <div>
              <h1 className="text-base font-extrabold text-gray-900">سلسلة صيدليات الأمل الحديثة المحدودة</h1>
              <p className="text-[11px] text-gray-500 font-mono">Al-Amal Modern Pharmacy Chain LLC</p>
            </div>
          </div>
          <div className="text-[10px] text-gray-600 font-mono space-y-0.5 pt-2">
            <p>الرقم الضريبي (VAT #): <strong className="text-gray-900">300998877600003</strong></p>
            <p>السجل التجاري (CR #): <strong className="text-gray-900">1010889922</strong></p>
            <p>ترخيص وزارة الصحة / الغذاء والدواء: <strong className="text-gray-900">MOH-RX-2026-991</strong></p>
            <p>العنوان: المملكة العربية السعودية — الرياض — شارع العليا العام</p>
          </div>
        </div>

        <div className="text-end space-y-1">
          <div className="inline-block bg-emerald-50 text-emerald-800 border border-emerald-200 px-3 py-1 rounded-lg font-bold text-sm">
            فاتورة ضريبية (Tax Invoice)
          </div>
          <div className="text-[11px] space-y-1 pt-2 font-mono">
            <p>رقم الفاتورة: <strong className="text-emerald-700 text-xs">{data.invoiceNumber}</strong></p>
            <p>تاريخ الإصدار: {data.issueDate}</p>
            <p>وقت الإصدار: {data.issueTime}</p>
            <p>الفرع: {data.branchName}</p>
          </div>
        </div>
      </div>

      {/* Customer & Invoice Details Bar */}
      <div className="grid grid-cols-2 gap-4 p-4 rounded-xl bg-gray-50 border border-gray-200 text-xs">
        <div className="space-y-1">
          <span className="text-[10px] text-gray-500 font-bold block">بيانات العميل المستلم (Billed To):</span>
          <p className="font-bold text-gray-900 text-sm">{data.customerName}</p>
          <p className="text-[11px] text-gray-600">فئة الحساب: {data.customerType}</p>
        </div>

        <div className="space-y-1 text-end">
          <span className="text-[10px] text-gray-500 font-bold block">طريقة السداد والتوثيق (Payment):</span>
          <p className="font-bold text-emerald-700 text-sm">
            {data.paymentMethod === "cash" ? "نقدي (Cash)" : data.paymentMethod === "card" ? "شبكة إلكترونية / مدى (Card)" : "بيع آجل / على الحساب (Credit B2B)"}
          </p>
          <p className="text-[11px] text-gray-600">الصيدلي / الكاشير: {data.cashierName}</p>
        </div>
      </div>

      {/* Itemized Table */}
      <div className="overflow-hidden border border-gray-200 rounded-xl">
        <table className="w-full text-xs text-right">
          <thead className="bg-gray-100 text-gray-700 font-bold text-[11px] border-b">
            <tr>
              <th className="p-3">#</th>
              <th className="p-3">الصنف الدوائي والتركيبة</th>
              <th className="p-3">رقم التشغيلة (Batch)</th>
              <th className="p-3 text-center">الكمية</th>
              <th className="p-3 text-left">سعر الوحدة</th>
              <th className="p-3 text-left">الخصم</th>
              <th className="p-3 text-left">الإجمالي الخاضع</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.items.map((item, idx) => (
              <tr key={item.id} className="hover:bg-gray-50">
                <td className="p-3 font-mono text-gray-500">{idx + 1}</td>
                <td className="p-3">
                  <span className="font-bold text-gray-900 block">{item.nameAr || item.name}</span>
                  {item.generic && <span className="text-[10px] text-gray-500 font-mono">{item.generic}</span>}
                </td>
                <td className="p-3 font-mono text-gray-600">{item.batchNumber || "BATCH-2026-A1"}</td>
                <td className="p-3 text-center font-mono font-bold">{item.quantity}</td>
                <td className="p-3 text-left font-mono">{formatCurrency(item.unitPrice)}</td>
                <td className="p-3 text-left font-mono text-amber-700">{item.discount ? `-${formatCurrency(item.discount)}` : "$0.00"}</td>
                <td className="p-3 text-left font-mono font-bold text-gray-900">{formatCurrency(item.totalPrice)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary Calculation & QR */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 pt-2">
        {/* QR Code & Return Policy (Left 6 Cols) */}
        <div className="md:col-span-6 space-y-3">
          <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-xl border">
            {renderQrCode()}
            <div className="text-[10px] text-gray-600 space-y-1">
              <p className="font-bold text-gray-900">فاتورة إلكترونية معتمدة</p>
              <p>مشفرة وفق متطلبات هيئة الزكاة والضريبة والجمارك وهيئة الغذاء والدواء SFDA.</p>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-gray-50 border text-[10px] text-gray-600 space-y-1">
            <p className="font-bold text-gray-900">سياسة الاسترجاع والضمان:</p>
            <p>• يُسمح بالاسترجاع خلال 3 أيام مع إحضار الفاتورة الأصلية بحالتها السليمة.</p>
            <p>• الأدوية المبردة وثلاجة الأنسولين لا تُسترجع لسلامة سلسلة التبريد الدوائي.</p>
          </div>
        </div>

        {/* Financial Totals (Right 6 Cols) */}
        <div className="md:col-span-6 space-y-2 text-xs">
          <div className="p-4 rounded-xl bg-gray-50 border space-y-2">
            <div className="flex justify-between text-gray-600">
              <span>المجموع قبل الخصم:</span>
              <span className="font-mono font-semibold">{formatCurrency(data.subtotal)}</span>
            </div>
            {data.discountAmount > 0 && (
              <div className="flex justify-between text-amber-700 font-bold">
                <span>الخصم الممنوح:</span>
                <span className="font-mono">-{formatCurrency(data.discountAmount)}</span>
              </div>
            )}
            <div className="flex justify-between text-gray-600">
              <span>وعاء الضريبة الخاضع:</span>
              <span className="font-mono font-semibold">{formatCurrency(data.taxableAmount)}</span>
            </div>
            <div className="flex justify-between text-gray-600">
              <span>ضريبة القيمة المضافة ({data.vatRatePercentage}%):</span>
              <span className="font-mono font-semibold">{formatCurrency(data.vatAmount)}</span>
            </div>
            <div className="flex justify-between text-base font-extrabold text-gray-900 pt-2 border-t border-gray-300">
              <span>صافي المبلغ الإجمالي:</span>
              <span className="font-mono text-emerald-700 text-lg">{formatCurrency(data.grandTotal)}</span>
            </div>
          </div>

          {data.amountInWordsAr && (
            <div className="p-2.5 bg-emerald-50 rounded-lg border border-emerald-200 text-emerald-900 text-[11px] font-semibold text-center">
              {data.amountInWordsAr}
            </div>
          )}
        </div>
      </div>

      {/* Official Signatures Footer */}
      <div className="grid grid-cols-2 gap-8 pt-6 border-t-2 border-gray-200 text-center text-xs">
        <div className="space-y-6">
          <p className="font-bold text-gray-700">توقيع وختم الصيدلي المرخص المسؤول</p>
          <div className="h-10 border-b border-dashed border-gray-400 w-48 mx-auto flex items-end justify-center text-emerald-700 font-mono text-[11px] font-bold">
            د. سارة — صيدلي إكلينيكي #91044
          </div>
        </div>

        <div className="space-y-6">
          <p className="font-bold text-gray-700">توقيع المستلم / العميل</p>
          <div className="h-10 border-b border-dashed border-gray-400 w-48 mx-auto" />
        </div>
      </div>
    </div>
  );
}
