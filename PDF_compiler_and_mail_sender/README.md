# PDF Compiler and Mail Sender

Welcome to the **PDF Compiler and Mail Sender** branch of the Learning Python repository. This folder contains tools designed to streamline invoice management by automating PDF compilation and email delivery.

## Folder Structure
This branch contains the following components:

- **`fattura_base_compilabile.pdf`**: A base invoice template in PDF format, ready to be filled with data.
- **`Windows 11/`**: Contains programs and dependencies for Windows 11.
- **`macOS/`**: Contains programs and dependencies for macOS.

Each operating system folder includes:
- **Program 1: PDF Compiler**
- **Program 2: Mail Sender**
- Required files, fonts and dependencies for proper execution.

## Program Descriptions

### 1. PDF Compiler
The PDF Compiler automates the process of populating the `fattura_base.pdf` template using data from an Excel file (e.g., invoice details).

#### Features:
- **Field Mapping**: Inserts data into predefined areas of the PDF template.
- **File Compression**: Reduces the size of the generated PDFs to optimize performance and storage.
- **Font Selection**: Fonts can be customized from the provided `fonts/` folder or manually updated in the program.
- **Batch Processing**: Handles large datasets without overloading the system, making it ideal for creating multiple invoices.

#### Output:
The program generates lightweight, ready-to-use PDF invoices.

### 2. Mail Sender
The Mail Sender automates the process of sending invoices created with the PDF Compiler to clients via email.

#### Features:
- **Email Automation**: Sends the corresponding invoice to the client's email address, as specified in the Excel file.
- **Customizable Messages**: Allows you to personalize the email content directly from the program.
- **Security**: Requires the Gmail password to be stored as an environment variable for improved security.
- **Usage Limits**: Adheres to Gmail's sending limits to avoid account issues.

#### How it Works:
1. Matches the generated invoice (by name) to the client's email address from the Excel file.
2. Sends the email with the attached invoice and a custom message.
3. Performs validation to ensure the file and email match correctly.

## Recommendations
- **Security**: Store the Gmail password securely as an environment variable to protect sensitive information.
- **Usage**: Ensure to stay within Gmail's daily sending limits to avoid temporary restrictions.
- **Customization**: Fonts and email templates can be modified to suit your needs.

## Getting Started
1. **Clone the Repository**
   ```bash
   git clone https://github.com/AstroTeo99/learning_python.git
   ```
   Navigate to the `PDF_compiler_and_mail_sender` folder.

2. **Choose Your Platform**
   Select the appropriate folder (`Windows 11/` or `macOS/`) for your operating system.

3. **Set Environment Variables**
   - Define your Gmail password as an environment variable for the Mail Sender program.

4. **Run the Programs**
   - Follow the instructions in the README file inside the platform-specific folder to execute the tools.

## License
This project is distributed under the [MIT](../LICENSE) license. Feel free to use, modify, and distribute it in accordance with the license terms.

---

If you have any suggestions or run into issues, feel free to open an Issue or Pull Request.
