import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class GestorFinanceiroOficial:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor Financeiro - Oficial")
        self.root.geometry("1180x950")
        self.root.configure(bg="#f4f4f9")
        
        self.config_db()
        self.config_ui()
        self.atualizar_visualizacao()

    def config_db(self):
        self.conn = sqlite3.connect('financeiro_permanente.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lancamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT, descricao TEXT, valor REAL, 
                categoria TEXT, metodo TEXT, parcela_info TEXT, 
                mes TEXT, ano TEXT
            )
        ''')
        self.conn.commit()

    def config_ui(self):
        # Cabeçalho
        self.f_header = tk.Frame(self.root, bg="#1a242f", pady=20)
        self.f_header.pack(fill="x")
        
        self.lbl_sugestao = tk.Label(self.f_header, text="Meta de Reserva: R$ 0.00", font=("Arial", 11, "italic"), bg="#1a242f", fg="#2ecc71")
        self.lbl_sugestao.pack()

        # Label Renda + Aux
        self.lbl_resumo_topo = tk.Label(self.f_header, text="RENDA + AUX: R$ 0.00 | GASTOS TOTAIS: R$ 0.00", 
                                        font=("Arial", 12, "bold"), bg="#1a242f", fg="white", pady=5)
        self.lbl_resumo_topo.pack()

        self.lbl_saldo_real = tk.Label(self.f_header, text="SALDO EM CONTA (LIVRE): R$ 0.00", 
                                       font=("Arial", 16, "bold"), bg="#1a242f", fg="#3498db")
        self.lbl_saldo_real.pack(pady=5)

        self.lbl_reserva_total = tk.Label(self.f_header, text="RESERVA ACUMULADA: R$ 0.00", font=("Arial", 14, "bold"), bg="#1a242f", fg="#f1c40f")
        self.lbl_reserva_total.pack()

        # Cadastro de Movimentações
        f_input = tk.LabelFrame(self.root, text=" Cadastro de Movimentações ", padx=10, pady=10, bg="#f4f4f9")
        f_input.pack(fill="x", padx=20, pady=10)

        tk.Label(f_input, text="Descrição:", bg="#f4f4f9").grid(row=0, column=0)
        self.ent_desc = tk.Entry(f_input, width=18); self.ent_desc.grid(row=0, column=1, padx=5)

        tk.Label(f_input, text="Valor R$:", bg="#f4f4f9").grid(row=0, column=2)
        self.ent_valor = tk.Entry(f_input, width=10); self.ent_valor.grid(row=0, column=3, padx=5)

        tk.Label(f_input, text="Categoria:", bg="#f4f4f9").grid(row=0, column=4)
        self.lista_categorias = ["Salário", "Extra", "Auxílio Transporte", "Gastos Fixos", "Gastos Livres", "Assinaturas", "Supermercado", "Reserva/Investimento", "Moradia", "Lazer"]
        self.cb_cat = ttk.Combobox(f_input, values=self.lista_categorias, state="readonly", width=15); self.cb_cat.grid(row=0, column=5, padx=5); self.cb_cat.current(0)

        tk.Label(f_input, text="Operação:", bg="#f4f4f9").grid(row=1, column=0, pady=10)
        self.cb_metodo = ttk.Combobox(f_input, values=["Dinheiro/Débito", "Cartão de Crédito", "Retirada de Reserva"], state="readonly", width=15); self.cb_metodo.grid(row=1, column=1); self.cb_metodo.current(0)

        tk.Label(f_input, text="Parcelas:", bg="#f4f4f9").grid(row=1, column=2)
        self.cb_parcelas = ttk.Combobox(f_input, values=[str(i) for i in range(1, 49)], state="readonly", width=5); self.cb_parcelas.grid(row=1, column=3); self.cb_parcelas.current(0)

        self.meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        tk.Label(f_input, text="Mês:", bg="#f4f4f9").grid(row=1, column=4)
        self.cb_mes = ttk.Combobox(f_input, values=self.meses, state="readonly", width=10); self.cb_mes.grid(row=1, column=5); self.cb_mes.current(datetime.now().month - 1)
        
        tk.Label(f_input, text="Ano:", bg="#f4f4f9").grid(row=1, column=6)
        self.cb_ano = ttk.Combobox(f_input, values=[str(a) for a in range(2024, 2035)], state="readonly", width=7); self.cb_ano.grid(row=1, column=7, padx=5); self.cb_ano.set(str(datetime.now().year))

        btn_lancar = tk.Button(f_input, text="LANÇAR", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), command=self.lancar, width=10)
        btn_lancar.grid(row=1, column=8, padx=10)

        # Botões Coloridos 
        f_botoes = tk.Frame(self.root, bg="#f4f4f9")
        f_botoes.pack(fill="x", padx=20, pady=5)
        
        tk.Button(f_botoes, text="📋 RESUMO LISTADO MÊS", bg="#3498db", fg="white", font=("Arial", 9, "bold"), command=lambda: self.abrir_detalhamento("mes")).pack(side="left", padx=5)
        tk.Button(f_botoes, text="📅 RESUMO LISTADO ANO", bg="#9b59b6", fg="white", font=("Arial", 9, "bold"), command=lambda: self.abrir_detalhamento("ano")).pack(side="left", padx=5)
        tk.Button(f_botoes, text="🗑️ APAGAR SELECIONADO", bg="#e74c3c", fg="white", font=("Arial", 9, "bold"), command=self.deletar).pack(side="right", padx=5)

        # Tabela
        self.tree = ttk.Treeview(self.root, columns=("ID", "Tipo", "Descrição", "Valor", "Categoria", "Método", "Parcela", "Mês", "Ano"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col); self.tree.column(col, anchor="center", width=100)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

    def lancar(self):
        try:
            desc = self.ent_desc.get(); val = float(self.ent_valor.get().replace(",", ".")); cat = self.cb_cat.get(); met = self.cb_metodo.get(); parc = int(self.cb_parcelas.get())
            mes_idx = self.meses.index(self.cb_mes.get()); ano_val = int(self.cb_ano.get())
            
            tipo = "Entrada" if (cat in ["Salário", "Extra", "Auxílio Transporte"] or met == "Retirada de Reserva") else "Saída"
            
            # CRÉDITO: Pula para o mês seguinte se for Cartão de Crédito
            pulo = 1 if met == "Cartão de Crédito" else 0

            for i in range(parc):
                idx_total = mes_idx + i + pulo
                m_idx = idx_total % 12
                a_ref = ano_val + (idx_total // 12)
                self.cursor.execute("INSERT INTO lancamentos (tipo, descricao, valor, categoria, metodo, parcela_info, mes, ano) VALUES (?,?,?,?,?,?,?,?)", 
                                   (tipo, desc, val/parc, cat, met, f"{i+1}/{parc}", self.meses[m_idx], str(a_ref)))
            
            self.conn.commit(); self.atualizar_visualizacao(); self.ent_desc.delete(0, tk.END); self.ent_valor.delete(0, tk.END)
        except: messagebox.showerror("Erro", "Valor inválido.")

    def abrir_detalhamento(self, tipo_resumo):
        m, a = self.cb_mes.get(), self.cb_ano.get()
        query = "SELECT tipo, descricao, valor, categoria, metodo FROM lancamentos WHERE mes=? AND ano=?" if tipo_resumo == "mes" else "SELECT tipo, descricao, valor, categoria, metodo FROM lancamentos WHERE ano=?"
        params = (m, a) if tipo_resumo == "mes" else (a,)
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        
        ent, gas, res, t_e, t_g_deb, t_g_cred, t_r = "", "", "", 0, 0, 0, 0
        for r in rows:
            t, d, v, c, met = r
            if t == "Entrada" and c != "Retirada de Reserva":
                ent += f"• {d}: R$ {v:.2f}\n"; t_e += v
            elif t == "Saída" and c != "Reserva/Investimento":
                gas += f"• {d}: R$ {v:.2f}\n"
                if met == "Cartão de Crédito": t_g_cred += v
                else: t_g_deb += v
            elif c == "Reserva/Investimento" or met == "Retirada de Reserva":
                res += f"• {d}: R$ {v:.2f}\n"
                t_r += v if met != "Retirada de Reserva" else -v

        # Janela de texto
        win = tk.Toplevel(self.root)
        win.title("Detalhamento")
        win.geometry("400x600")
        txt = tk.Text(win, padx=10, pady=10, font=("Arial", 10), bg="white")
        txt.pack(expand=True, fill="both")
        
        conteudo = f"RESUMO {tipo_resumo.upper()} ({m}/{a})\n\nENTRADAS:\n{ent}TOTAL: R$ {t_e:.2f}\n\n"
        conteudo += f"GASTOS (Débito/Dinheiro):\nTOTAL: R$ {t_g_deb:.2f}\n\n"
        conteudo += f"GASTOS (Crédito - Não abate saldo):\nTOTAL: R$ {t_g_cred:.2f}\n\n"
        conteudo += f"RESERVA:\n{res}LÍQUIDO: R$ {t_r:.2f}\n\n"
        conteudo += f"💵 SALDO LIVRE EM CONTA: R$ {t_e - t_g_deb - (t_r if t_r > 0 else 0):.2f}"
        
        txt.insert("1.0", conteudo); txt.config(state="disabled")

    def deletar(self):
        sel = self.tree.selection()
        if sel:
            item_id = self.tree.item(sel)['values'][0]
            self.cursor.execute("DELETE FROM lancamentos WHERE id = ?", (item_id,))
            self.conn.commit(); self.atualizar_visualizacao()

    def atualizar_visualizacao(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        m, a = self.cb_mes.get(), self.cb_ano.get()
        self.cursor.execute("SELECT * FROM lancamentos WHERE mes=? AND ano=? ORDER BY id DESC", (m, a))
        rows = self.cursor.fetchall()
        
        r_m, g_tot, g_deb, gu_m, b_r = 0, 0, 0, 0, 0
        for r in rows:
            self.tree.insert("", "end", values=r)
            if r[1] == "Entrada":
                if r[4] in ["Salário", "Extra", "Auxílio Transporte"]:
                    r_m += r[3]
                    if r[4] != "Auxílio Transporte": b_r += r[3]
            elif r[1] == "Saída" and r[4] != "Reserva/Investimento":
                g_tot += r[3]
                if r[5] != "Cartão de Crédito": g_deb += r[3]
            elif r[4] == "Reserva/Investimento": gu_m += r[3]
            elif r[5] == "Retirada de Reserva": gu_m -= r[3]

        s_r = r_m - g_deb - (gu_m if gu_m > 0 else 0)
        self.lbl_sugestao.config(text=f"Meta de Reserva ({m}/{a}): R$ {b_r*0.20:.2f}")
        self.lbl_resumo_topo.config(text=f"RENDA + AUX: R$ {r_m:.2f} | GASTOS TOTAIS: R$ {g_tot:.2f}")
        self.lbl_saldo_real.config(text=f"SALDO EM CONTA (LIVRE): R$ {s_r:.2f}")
        
        self.cursor.execute("SELECT SUM(valor) FROM lancamentos WHERE categoria='Reserva/Investimento'")
        tg = self.cursor.fetchone()[0] or 0
        self.cursor.execute("SELECT SUM(valor) FROM lancamentos WHERE metodo='Retirada de Reserva'")
        tr = self.cursor.fetchone()[0] or 0
        self.lbl_reserva_total.config(text=f"RESERVA ACUMULADA: R$ {tg - tr:.2f}")

if __name__ == "__main__":
    root = tk.Tk(); app = GestorFinanceiroOficial(root); root.mainloop()