from pikepdf import Pdf
import glob
import pikepdf
import os

def get_sorted_pdfs(filepath):
    """Get sorted list of pdf-files in a folder. Sorted by number.
            
    Keyword arguments:
        filepath[String] -- path to the folder containing the pdf-files
    Returns: 
        sortedPdfList[List] -- List of the pdf-paths in sorted order
    """
    pdfs = glob.glob(filepath)
    myrange = len(pdfs)
    pdfDict = {}
    for _ in range(myrange):
        if pdfs:
            file = pdfs.pop(0)
            number = os.path.split(file)[1].split('.pdf')[0]
            pdfDict[file] = int(number)
    sortedPdfList = sorted(pdfDict, key=pdfDict.get)
    return sortedPdfList

def sort_and_merge_pdfs(filepath, output_folder, output_name):
    """Merge all pdf-files in folder in sorted order.

    Keyword arguments:
        filepath[String] -- path to the folder containing the pdf-files
        output_folder[String] -- path to the output-folder for merged pdf
        output_name[String] -- name of the merged pdf (NOTE: Do not includ ".pdf" in the name)
    """
    mergelist = get_sorted_pdfs(filepath)
    if mergelist:
        mergedPdf = Pdf.new()
        #merger = PdfFileMerger()
        for pdf in mergelist:
            try:
                input = Pdf.open(pdf)
                mergedPdf.pages.extend(input.pages)
            except pikepdf._qpdf.PdfError:
                print('Error trying to merge {}.\nThis is most likely not a pdf-file. Skipping this file!'.format(pdf))
            except Exception as e:
                print('Unexpected error: {}'.format(e))
                raise e
        mergedPdf.save(os.path.join(output_folder, '{}.pdf'.format(output_name)))
    else:
        print("mergelist is empty please check your input path")