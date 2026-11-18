3x3 MATRIX OPERATIONS PROJECT
=============================

Two versions:
1) Version_1_Without_NumPy: pure Python lists and loops.
2) Version_2_With_NumPy: NumPy arrays and NumPy functions.

Each version includes:
- CMD/terminal program
- Tkinter GUI program

Operations:
Addition, subtraction, matrix multiplication, element-wise multiplication,
transpose, determinant, inverse, trace, scalar multiplication, equality check.

RUN WITHOUT NUMPY:
Open terminal in Version_1_Without_NumPy:
    python matrix_cmd.py
    python matrix_gui.py

RUN WITH NUMPY:
Install NumPy:
    python -m pip install numpy

Open terminal in Version_2_With_NumPy:
    python matrix_cmd.py
    python matrix_gui.py

GUI:
Enter values in the 3x3 cells of Matrix A and Matrix B.
Choose an operation from the dropdown. For scalar multiplication, enter
the scalar beside the dropdown. Click Calculate.

Notes:
- Python 3 is required.
- Tkinter is included with most standard Python installations.
- Inverse is only possible when determinant is non-zero.
- Matrix multiplication uses A × B.
- Transpose, determinant, inverse, and trace are calculated for Matrix A.
