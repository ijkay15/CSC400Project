from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
c = canvas.Canvas('ex.pdf')
c.drawString(100,100, "Merry Had A LIttle Lamb")
c.showPage()
#c.save()