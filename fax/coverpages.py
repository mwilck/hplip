# -*- coding: utf-8 -*-
#
# (c) Copyright 2003-2006 Hewlett-Packard Development Company, L.P.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# Author: Don Welch
#

from reportlab.platypus.paragraph import Paragraph  
from reportlab.platypus.doctemplate import *
from reportlab.platypus import SimpleDocTemplate, Spacer
from reportlab.platypus.tables import Table, TableStyle #, LIST_STYLE

from reportlab.lib.pagesizes import letter, legal, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors

from time import localtime, strftime

from base import utils

PAGE_SIZE_LETTER = 'letter'
PAGE_SIZE_LEGAL = 'legal'
PAGE_SIZE_A4 = 'a4'


def createStandardCoverPage(page_size=PAGE_SIZE_LETTER,
                            total_pages=1, 
                            
                            recipient_name='', 
                            recipient_phone='', 
                            recipient_fax='', 
                            
                            sender_name='', 
                            sender_phone='',
                            sender_fax='', 
                            sender_email='', 
                            
                            regarding='', 
                            message=''):

                    
    s = getSampleStyleSheet()
    
    story = []
    
    ps = ParagraphStyle(name="title", 
                        parent=None, 
                        fontName='helvetica-bold',
                        fontSize=36,
                        )

    story.append(Paragraph("Fax", ps))
    
    story.append(Spacer(1, inch))
    
    ps = ParagraphStyle(name='normal',
                        fontName='Times-Roman',
                        fontSize=12) #,
                        #leading=12)
    
    
    recipient_name_label = Paragraph("To:", ps)
    recipient_name_text = Paragraph(recipient_name[:64], ps)
    
    recipient_fax_label = Paragraph("Fax:", ps)
    recipient_fax_text = Paragraph(recipient_fax[:64], ps)
    
    recipient_phone_label = Paragraph("Phone:", ps)
    recipient_phone_text = Paragraph(recipient_phone[:64], ps)
    
    
    sender_name_label = Paragraph("From:", ps)
    sender_name_text = Paragraph(sender_name[:64], ps)

    sender_phone_label = Paragraph("Phone:", ps)
    sender_phone_text = Paragraph(sender_phone[:64], ps)
    
    sender_email_label = Paragraph("Email:", ps)
    sender_email_text = Paragraph(sender_email[:64], ps)
    
    
    regarding_label = Paragraph("Regarding:", ps)
    regarding_text = Paragraph(regarding[:128], ps)
    
    date_time_label = Paragraph("Date:", ps)
    date_time_text = Paragraph(strftime("%a, %d %b %Y %H:%M:%S (%Z)", localtime()), ps)
    
    total_pages_label = Paragraph("Total Pages:", ps)
    total_pages_text = Paragraph("%d" % total_pages, ps)

    data = [[recipient_name_label, recipient_name_text, sender_name_label, sender_name_text],
            [recipient_fax_label, recipient_fax_text, sender_phone_label, sender_phone_text],
            #[recipient_phone_label, recipient_phone_text, sender_email_label, sender_email_text],
            [date_time_label, date_time_text, sender_email_label, sender_email_text],
            #[ '', '', date_time_label, date_time_text],
            [regarding_label, regarding_text, total_pages_label, total_pages_text]]
            
    LIST_STYLE = TableStyle([('LINEABOVE', (0,0), (-1,0), 2, colors.black),
                             ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
                             ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black),
                             ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
                             ('VALIGN', (0, 0), (-1, -1), 'TOP'), 
                            ])
    
    t = Table(data, style=LIST_STYLE)
   
    story.append(t)
    
    if message:
        
        MSG_STYLE = TableStyle([('LINEABOVE', (0,0), (-1,0), 2, colors.black),
                                 ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
                                 ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black),
                                 ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
                                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                 ('SPAN', (-2, 1), (-1, -1)), 
                                ])
    
        story.append(Spacer(1, 0.5*inch))
        
        data = [[Paragraph("Comments/Notes:", ps), ''],
                [Paragraph(message[:2048], ps), ''],]
                
        t = Table(data, style=MSG_STYLE)
        
        story.append(t)
    
    if page_size == PAGE_SIZE_LETTER:
        pgsz = letter
    elif page_size == PAGE_SIZE_LEGAL:
        pgsz = legal
    else:
        pgsz = A4
        
    f_fd, f = utils.make_temp_file()
    
    doc = SimpleDocTemplate(f, pagesize=pgsz)
    doc.build(story)
    
    return f
    
    
    
#            { "name" : (function, "thumbnail.png"), ... }    
COVERPAGES = { "basic": (createStandardCoverPage, 'standard_coverpage.png'),
             }
 
