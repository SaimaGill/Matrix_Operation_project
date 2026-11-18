import numpy as np

def read_matrix(name):
    print(f"\nEnter values for Matrix {name} (3 rows, 3 numbers each):")
    rows=[]
    for i in range(3):
        while True:
            try:
                row=list(map(float,input(f"Row {i+1}: ").split()))
                if len(row)==3: rows.append(row); break
                print("Enter exactly 3 numbers.")
            except ValueError: print("Invalid numbers. Try again.")
    return np.array(rows,dtype=float)

def main():
    print("3x3 MATRIX OPERATIONS - WITH NUMPY")
    A,B=read_matrix("A"),read_matrix("B")
    while True:
        print("\n1 Addition  2 Subtraction  3 Matrix Multiplication")
        print("4 Element-wise Multiplication  5 Transpose A")
        print("6 Determinant A  7 Inverse A  8 Trace A")
        print("9 Scalar Multiplication A  10 Equality  0 Exit")
        choice=input("Select operation: ").strip()
        try:
            if choice=="1": result=A+B
            elif choice=="2": result=A-B
            elif choice=="3": result=A@B
            elif choice=="4": result=A*B
            elif choice=="5": result=A.T
            elif choice=="6": result=np.linalg.det(A)
            elif choice=="7": result=np.linalg.inv(A)
            elif choice=="8": result=np.trace(A)
            elif choice=="9": result=A*float(input("Enter scalar: "))
            elif choice=="10": result="Matrices are equal." if np.array_equal(A,B) else "Matrices are not equal."
            elif choice=="0": print("Goodbye!"); break
            else: print("Invalid option."); continue
            print("\nResult:\n",result)
        except np.linalg.LinAlgError: print("Error: Matrix is singular; inverse does not exist.")
        except ValueError as e: print("Error:",e)
if __name__=="__main__": main()
