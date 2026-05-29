# Custom QR Code Generator

A Python script that generates various styles of QR codes. You can create everything from a basic black-and-white QR code to advanced versions with custom gradient colors and an embedded logo, all in a single run.

## ✨ Features

<table>
<tr>
<td align="center">
<img src="images/permanent_qr_basic.png" width="250"><br>
<b>Basic QR Code</b>
</td>

<td align="center">
<img src="images/permanent_qr_gradient.png" width="250"><br>
<b>Gradient QR Code</b>
</td>

<td align="center">
<img src="images/permanent_qr_gradient_icon.png" width="250"><br>
<b>Icon Embedded QR Code</b>
</td>
</tr>
</table>

### Basic QR Code (`permanent_qr_basic.png`)
Generates a standard black-and-white QR code with a high error correction rate (**Error Correction Level H**).

### Gradient QR Code (`permanent_qr_gradient.png`)
Applies a vertical gradient (blue → olive). It maintains square internal modules while using rounded eyes (the three corner markers) for a cleaner and more modern appearance.

### Icon Embedded QR Code (`permanent_qr_gradient_icon.png`)
Embeds a user-specified logo or icon (`icon.png`) in the center of the gradient QR code. A white margin is automatically added around the icon to ensure reliable scanning performance.

---

## 🛠 Dependencies

Install the required packages:

```bash
conda create -n qrgen python=3.10 -y 
conda activate qrgen
pip install "qrcode[pil]" Pillow
```

---

## 🚀 Usage

### 1. Set the Data

Modify the `data` variable in the script to the URL or text you want to encode.

```python
data = "https://github.com/ISL-Lab/ISLLab_QR_Generator"
```

### 2. Prepare an Icon (Optional)

To embed an image in the center of the QR code, place an `icon.png` file in the same directory as the script.

If no icon is found, the script will generate the basic and gradient QR codes and automatically skip the icon version.

### 3. Customize Colors & Styles (Optional)

- Modify `top_color` and `bottom_color` to change the gradient colors. If you use Visual Studio Code, you can conveniently choose colors using the built-in color picker. Simply click on the color value (e.g., `#185A99`) while editing the script, and VS Code will open a color palette for visual selection.
```python
top_hex_color = "#185A99"
bottom_hex_color = "#92A73F"
```

- Adjust `icon_padding_ratio` to control the size of the white margin around the embedded icon.
```python
icon_padding_ratio = 0.01
```

### 4. Run the Script

```bash
cd ISLLab_QR_Generator
python qr_gradient.py
```

---

## 📁 Output Files

| File Name | Description |
|------------|-------------|
| `permanent_qr_basic.png` | Standard black-and-white QR code |
| `permanent_qr_gradient.png` | Vertical gradient QR code with rounded eye markers |
| `permanent_qr_gradient_icon.png` | Gradient QR code with an embedded `icon.png` logo |