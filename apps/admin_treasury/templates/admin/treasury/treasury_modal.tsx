import React from 'react';
import { X, FileText, CheckCircle2, ShieldCheck, Printer, ArrowDownLeft, ArrowUpRight } from 'lucide-react';
import { TreasuryTransaction } from '../../../../../src/types';

interface TreasuryModalProps {
  transaction: TreasuryTransaction | null;
  onClose: () => void;
}

export const TreasuryModalComponent: React.FC<TreasuryModalProps> = ({ transaction, onClose }) => {
  if (!transaction) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs">
      <div className="bg-white w-full max-w-2xl rounded-3xl shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="bg-[#4A154B] text-white p-6 flex items-start justify-between">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-white/20 text-amber-300 text-xs font-mono font-bold">
              <ShieldCheck className="w-3.5 h-3.5" />
              سند قيد دفتري معتمد
            </div>
            <h3 className="text-xl font-black font-mono tracking-tight">{transaction.refCode}</h3>
            <p className="text-xs text-purple-200 font-mono">رقم السند: {transaction.voucherNumber}</p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Amount Box */}
          <div className="p-4 rounded-2xl bg-purple-50/50 border border-purple-100 flex items-center justify-between">
            <div>
              <span className="text-xs text-slate-500 block">المبلغ المعتمد في القيد</span>
              <div className="text-2xl font-black font-mono text-slate-900 mt-0.5">
                <span className={transaction.flowType === 'inflow' ? 'text-emerald-600' : 'text-rose-600'}>
                  {transaction.flowType === 'inflow' ? '+' : '-'}
                  {transaction.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
                <span className="text-xs font-bold text-slate-500 font-sans mr-1">SAR</span>
              </div>
            </div>

            <div className="text-left">
              <span className="text-xs text-slate-500 block">نوع التدفق</span>
              <span
                className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold mt-1 ${
                  transaction.flowType === 'inflow'
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-rose-100 text-rose-800'
                }`}
              >
                {transaction.flowType === 'inflow' ? <ArrowDownLeft className="w-3.5 h-3.5" /> : <ArrowUpRight className="w-3.5 h-3.5" />}
                {transaction.flowType === 'inflow' ? 'تدفق وارد (+)' : 'تدفق صادر (-)'}
              </span>
            </div>
          </div>

          {/* Grid Details */}
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-500 block">التصنيف</span>
              <span className="font-bold text-slate-900 mt-1 block">{transaction.categoryName}</span>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-500 block">التاريخ والوقت</span>
              <span className="font-mono font-bold text-slate-900 mt-1 block">{transaction.createdAt}</span>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-500 block">الطرف المقابل / الحساب</span>
              <span className="font-bold text-slate-900 mt-1 block">{transaction.sourceDestination}</span>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-500 block">الرصيد بعد الحركة</span>
              <span className="font-mono font-bold text-[#4A154B] mt-1 block">
                {transaction.balanceAfter.toLocaleString(undefined, { minimumFractionDigits: 2 })} SAR
              </span>
            </div>
          </div>

          {/* Description */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs">
            <span className="font-bold text-slate-800 block mb-1">البيان والشرح المحاسبي:</span>
            <p className="text-slate-600 leading-relaxed">{transaction.description}</p>
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-slate-200">
            <button
              onClick={() => window.print()}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl transition flex items-center gap-1.5"
            >
              <Printer className="w-4 h-4" />
              طباعة السند
            </button>
            <button
              onClick={onClose}
              className="px-5 py-2 bg-[#4A154B] hover:bg-[#3F0E40] text-white text-xs font-bold rounded-xl transition"
            >
              إغلاق
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
