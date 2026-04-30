import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.metrics import r2_score
from scipy.optimize import curve_fit
import tkinter as tk
from tkinter import filedialog, messagebox
import warnings
import os

from .models import mzi_model, diode_model

warnings.filterwarnings('ignore')

class XMLAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Integrated XML Analyzer - Advanced Analysis")
        self.root.geometry("1400x1000")

        self.top_frame = tk.Frame(root)
        self.top_frame.pack(pady=10)

        tk.Label(self.top_frame, text="Script Owner:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.owner_var = tk.StringVar(value="")
        self.owner_entry = tk.Entry(self.top_frame, textvariable=self.owner_var, width=15, font=("Arial", 10))
        self.owner_entry.pack(side=tk.LEFT, padx=10)

        self.btn_browse = tk.Button(self.top_frame, text="데이터 파일 불러오기", command=self.load_file,
                                    width=22, height=2, bg="#f0f0f0", font=("Arial", 10, "bold"))
        self.btn_browse.pack(side=tk.LEFT, padx=10)

        self.btn_export = tk.Button(self.top_frame, text="데이터 결과 저장", command=self.save_to_excel,
                                    width=22, height=2, bg="#4CAF50", fg="white", state=tk.DISABLED,
                                    font=("Arial", 10, "bold"))
        self.btn_export.pack(side=tk.LEFT, padx=10)

        self.filename_var = tk.StringVar(value="파일을 선택해주세요.")
        self.filename_label = tk.Label(root, textvariable=self.filename_var, font=("Arial", 11, "bold"), fg="#333333")
        self.filename_label.pack(pady=5)

        self.info_label = tk.Label(root, text="분석을 시작하려면 파일을 선택하세요.", font=("Arial", 10), fg="gray")
        self.info_label.pack(pady=2)

        self.nav_frame = tk.Frame(root)
        self.nav_frame.pack(fill=tk.X, padx=50, pady=10)

        self.btn_prev = tk.Button(self.nav_frame, text="◀◀ 이전 사이트", command=self.show_prev_site, width=15,
                                  state=tk.DISABLED)
        self.btn_prev.pack(side=tk.LEFT)

        self.status_label = tk.Label(self.nav_frame, text="사이트 0 / 0", font=("Arial", 11, "bold"), fg="blue")
        self.status_label.pack(side=tk.LEFT, expand=True)

        self.btn_next = tk.Button(self.nav_frame, text="다음 사이트 ▶▶", command=self.show_next_site, width=15,
                                  state=tk.DISABLED)
        self.btn_next.pack(side=tk.RIGHT)

        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.canvas = None
        self.analysis_df = None
        self.sites_plot_data = []
        self.current_site_index = 0

    def load_file(self):
        file_paths = filedialog.askopenfilenames(title="통합 XML 파일 선택",
                                                 filetypes=(("XML files", "*.xml"), ("all files", "*.*")))
        if file_paths:
            if len(file_paths) == 1:
                self.filename_var.set(os.path.basename(file_paths[0]))
            else:
                self.filename_var.set(f"{os.path.basename(file_paths[0])} 외 {len(file_paths) - 1}개 파일")
            self.process_multiple_data(file_paths)

    def process_multiple_data(self, file_paths):
        all_sites_data = []
        self.sites_plot_data = []
        error_count = 0

        for file_path in file_paths:
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()

                ref_node = root.find(".//Modulator[@Name='DCM_LMZC_ALIGN']")
                if ref_node is None: ref_node = root

                ref_ws = ref_node.find(".//WavelengthSweep")
                wl_ref = np.array([float(s) for s in ref_ws.find('L').text.split(',')])
                il_ref = np.array([float(s) for s in ref_ws.find('IL').text.split(',')])

                elements = root.findall('.//TestElement')
                if not elements: elements = [root]

                for element in elements:
                    site_info = element.find('.//TestSiteInfo')
                    dev_info = element.find('.//DeviceInfo')

                    site_attr = site_info.attrib if site_info is not None else {}
                    dev_attr = dev_info.attrib if dev_info is not None else {}

                    mzm_sweeps = []
                    for ws in element.findall(".//WavelengthSweep"):
                        mzm_sweeps.append({
                            'L': np.array([float(s) for s in ws.find('L').text.split(',')]),
                            'IL': np.array([float(s) for s in ws.find('IL').text.split(',')]),
                            'Bias': ws.get('DCBias')
                        })

                    iv_node = element.find('.//IVMeasurement')
                    v, i = np.array([]), np.array([])
                    if iv_node is not None:
                        v = np.array([float(s) for s in iv_node.find('Voltage').text.split(',')])
                        i = np.array([float(s) for s in iv_node.find('Current').text.split(',')])

                    try:
                        p_ref = np.poly1d(np.polyfit(wl_ref, il_ref, 6))
                        rsq_ref = r2_score(il_ref, p_ref(wl_ref))
                    except:
                        rsq_ref = np.nan

                    try:
                        max_trans = np.max(il_ref)
                    except:
                        max_trans = np.nan

                    i_at_minus_1, i_at_1, rsq_iv = np.nan, np.nan, np.nan
                    if len(v) > 0 and len(i) > 0:
                        try:
                            idx_m1 = (np.abs(v - (-1.0))).argmin()
                            i_at_minus_1 = i[idx_m1]
                            idx_p1 = (np.abs(v - 1.0)).argmin()
                            i_at_1 = i[idx_p1]
                            p_iv = np.poly1d(np.polyfit(v, np.abs(i), 4))
                            rsq_iv = r2_score(np.abs(i), p_iv(v))
                        except:
                            pass

                    row_dict = {
                        'Lot': site_attr.get('Batch', ''),
                        'Wafer': site_attr.get('Wafer', ''),
                        'Mask': site_attr.get('Mask', 'LION1'),
                        'TestSite': site_attr.get('TestSite', ''),
                        'Name': dev_attr.get('Name', ''),
                        'Date': site_attr.get('Date', '2026.04.30'),
                        'Script ID': site_attr.get('ScriptID', 'process LMZC'),
                        'Script Ver': site_attr.get('ScriptVer', '0.1'),
                        'Script Owner': self.owner_var.get(),
                        'Operator': site_attr.get('Operator', ''),
                        'Row': site_attr.get('DieRow', '0'),
                        'Column': site_attr.get('DieColumn', '0'),
                        'ErrorFlag': '0',
                        'Error desc': 'No Error',
                        'Analysis Wavelength': 1550,
                        'Rsq of Ref. spectrum': rsq_ref,
                        'Max trans': max_trans,
                        'Rsq of IV': rsq_iv,
                        'I at -1V [A]': i_at_minus_1,
                        'I at 1V [A]': i_at_1
                    }

                    all_sites_data.append(row_dict)
                    self.sites_plot_data.append({
                        'wl_ref': wl_ref, 'il_ref': il_ref,
                        'mzm_sweeps': mzm_sweeps,
                        'iv_v': v, 'iv_i': i,
                        'res': row_dict
                    })

            except Exception as e:
                print(f"[{os.path.basename(file_path)}] 파일 처리 오류: {e}")
                error_count += 1
                continue

        if not all_sites_data:
            messagebox.showerror("오류", "분석 가능한 데이터가 없거나 파일이 잘못되었습니다.")
            return

        self.analysis_df = pd.DataFrame(all_sites_data)
        self.current_site_index = 0
        self.update_plot_display()
        self.btn_export.config(state=tk.NORMAL)

        msg = f"분석 완료: 총 {len(all_sites_data)}개 사이트 (선택된 파일 {len(file_paths)}개)"
        if error_count > 0:
            msg += f" / 오류 발생 파일: {error_count}개"
            self.info_label.config(text=msg, fg="red")
        else:
            self.info_label.config(text=msg, fg="blue")

    def plot_graphs(self, data):
        if self.canvas: self.canvas.get_tk_widget().destroy()

        fig, axes = plt.subplots(2, 3, figsize=(13, 8))
        plt.subplots_adjust(hspace=0.4, wspace=0.3)

        wl_ref, il_ref = data['wl_ref'], data['il_ref']
        mzm_sweeps = data['mzm_sweeps']
        iv_v, iv_i = data['iv_v'], data['iv_i']

        for s in mzm_sweeps:
            axes[0, 0].plot(s['L'], s['IL'], label=f"{s['Bias']}V", alpha=0.7)
        axes[0, 0].plot(wl_ref, il_ref, 'k', lw=1.5, label='Ref')
        axes[0, 0].set_title('1. MZM & Ref Spectra', fontsize=10, fontweight='bold')
        axes[0, 0].legend(fontsize=7, ncol=2)

        axes[0, 1].plot(wl_ref, il_ref, 'b.', markersize=1, alpha=0.3)
        for d in range(2, 7, 2):
            p = np.poly1d(np.polyfit(wl_ref, il_ref, d))
            axes[0, 1].plot(wl_ref, p(wl_ref), label=f'{d}th Fit')
        axes[0, 1].set_title('2. Ref Fitting', fontsize=10, fontweight='bold')
        axes[0, 1].legend(fontsize=8)

        poly_ref = np.poly1d(np.polyfit(wl_ref, il_ref, 6))
        for s in mzm_sweeps:
            il_f1 = s['IL'] - poly_ref(s['L'])
            top = il_f1 > np.percentile(il_f1, 90)
            p_res = np.poly1d(np.polyfit(s['L'][top], il_f1[top], 2))
            axes[0, 2].plot(s['L'], il_f1 - p_res(s['L']))
        axes[0, 2].set_title('3. Flat Spectra (2-step)', fontsize=10, fontweight='bold')
        axes[0, 2].set_ylim(-40, 5)

        target_v = "-1.0"
        mzm_1v = next((s for s in mzm_sweeps if s['Bias'] == target_v), None)
        if mzm_1v is not None:
            il_f1 = mzm_1v['IL'] - poly_ref(mzm_1v['L'])
            p_res = np.poly1d(np.polyfit(mzm_1v['L'][il_f1 > np.percentile(il_f1, 80)], il_f1[il_f1 > np.percentile(il_f1, 80)], 2))
            il_f2 = il_f1 - p_res(mzm_1v['L'])
            y_norm = 10 ** (il_f2 / 10)
            y_norm /= np.max(y_norm)
            try:
                popt, _ = curve_fit(mzi_model, mzm_1v['L'], y_norm, p0=[0.1, 0.9, 1550, 14, 0])
                axes[1, 0].plot(mzm_1v['L'], y_norm, 'b', alpha=0.4)
                axes[1, 0].plot(mzm_1v['L'], mzi_model(mzm_1v['L'], *popt), 'k--')
                axes[1, 0].set_title(f'4. MZI Fit ({target_v}V)', fontsize=10, fontweight='bold')
            except:
                pass

        if len(iv_v) > 0:
            axes[1, 1].semilogy(iv_v, np.abs(iv_i), 'bo', markersize=3)
        axes[1, 1].set_title('5. IV Raw (Log)', fontsize=10, fontweight='bold')

        if len(iv_v) > 0:
            axes[1, 2].semilogy(iv_v, np.abs(iv_i), 'ko', markersize=2, alpha=0.5)
            f_mask = iv_v >= 0.5
            if any(f_mask):
                try:
                    popt, _ = curve_fit(diode_model, iv_v[f_mask], np.abs(iv_i[f_mask]), p0=[1e-15, 1.3])
                    axes[1, 2].semilogy(iv_v[f_mask], diode_model(iv_v[f_mask], *popt), 'g-', lw=2, label='Diode Fit')
                except:
                    pass
            r_mask = iv_v <= 0.25
            if any(r_mask):
                p_rev = np.poly1d(np.polyfit(iv_v[r_mask], np.abs(iv_i[r_mask]), 4))
                axes[1, 2].semilogy(iv_v[r_mask], p_rev(iv_v[r_mask]), 'r-', label='Poly Fit')
            axes[1, 2].set_title('6. IV Advanced Fit', fontsize=10, fontweight='bold')
            axes[1, 2].legend(fontsize=7)

        self.canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_plot_display(self):
        total = len(self.sites_plot_data)
        if total == 0: return
        self.status_label.config(text=f"사이트 {self.current_site_index + 1} / {total}")
        self.btn_prev.config(state=tk.NORMAL if self.current_site_index > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.current_site_index < total - 1 else tk.DISABLED)
        self.plot_graphs(self.sites_plot_data[self.current_site_index])

    def show_next_site(self):
        self.current_site_index += 1
        self.update_plot_display()

    def show_prev_site(self):
        self.current_site_index -= 1
        self.update_plot_display()

    def save_to_excel(self):
        if self.analysis_df is None: return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=(("Excel", "*.xlsx"), ("All", "*.*")))
        if path:
            self.analysis_df.to_excel(path, index=False)
            messagebox.showinfo("저장 성공", "데이터 분석 결과가 저장되었습니다.")