from robocorp.tasks import task
from robocorp import browser, http
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive



tables = Tables()
pdf = PDF()
archive = Archive()


@task
def order_robots_from_RobotSpareBin():

  """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
  """
  open_robot_order_website()
  orders = get_orders()
  for order in orders:
    close_annoying_modal()
    order_number = fill_the_form(order)
    pdf_file = store_receipt_as_pdf(order_number)
    screenshot = screenshot_robot(order_number)
    embed_screenshot_to_receipt(screenshot, pdf_file)
    order_another_robot()
  archive_receipts()
        

def open_robot_order_website():
  browser.goto('https://robotsparebinindustries.com/#/robot-order')


def get_orders():
  file = http.download(url='https://robotsparebinindustries.com/orders.csv', overwrite=True)
  orders = tables.read_table_from_csv(path=file, header=True)
  return orders

def close_annoying_modal():
  page = browser.page()
  page.click('text=OK')

def fill_the_form(order):
  page = browser.page()
  page.select_option('#head', order['Head'])
  page.check(f'#id-body-{order["Body"]}')
  page.fill('.form-control', order['Legs'])
  page.fill('#address', order['Address'])
  page.click('#preview')
  while True:
    page.click('#order')
    if page.query_selector('#receipt'):
      break
      
  order_number = order['Order number']

  return order_number
 
def store_receipt_as_pdf(order_number):
  page = browser.page()
  receipt = page.locator('#receipt').inner_html()
  
  pdf.html_to_pdf(receipt, f'./output/receipts/receipt_{order_number}.pdf')
  pdf_file = f'./output/receipts/receipt_{order_number}.pdf'
  
  return pdf_file

def screenshot_robot(order_number):
  page = browser.page()
  robot_picture = page.locator('#robot-preview-image')
  robot_picture.screenshot(
    type='png',
    path=f'./output/receipts/images/screenshot_{order_number}.png'
    )

  screenshot = f'./output/receipts/images/screenshot_{order_number}.png'
  return screenshot

def embed_screenshot_to_receipt(screenshot, pdf_file):
  screenshot = [screenshot]
  pdf.add_files_to_pdf(screenshot, pdf_file, True)

def order_another_robot():
  page = browser.page()
  page.click('#order-another')
  
def archive_receipts():
  archive.archive_folder_with_zip('./output/receipts', './output/receipts.zip')