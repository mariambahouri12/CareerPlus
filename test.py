import pymupdf

pdf = pymupdf.open("Architecutre.pdf")

page = pdf[0]
pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))

pix.save("Architecture.png")

pdf.close()