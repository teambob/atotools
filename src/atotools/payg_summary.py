import sys
import json

SUPPLIER_DATA_RECORD1 = "628IDENTREGISTER1{abn:>011d}{run_type:<1.1s}{report_end_date:8.8s}EAPFEMPA011.0{empty:578.578s}"
SUPPLIER_DATA_RECORD2 = "628IDENTREGISTER2{name:<200.200s}{contact_name:<38.38s}{telephone_number:<15.15s}{fax_number:<15.15s}{file_reference:<16.16s}{empty:327.327s}"
SUPPLIER_DATA_RECORD3 = "628IDENTREGISTER3{street_address1:<38.38s}{street_address2:<38.38s}{street_suburb:<27.27s}{street_state:<3.3s}{street_postcode:>04d}{street_country:<20.20s}" \
    "{postal_address1:<38.38s}{postal_address2:<38.38s}{postal_suburb:<27.27s}{postal_state:<3.3s}{postal_postcode:>04d}{postal_country:<20.20s}{email:<76.76s}{empty:275.275}"
  
PAYER_IDENTITY_RECORD = "628IDENTITY{abn:>011d}{branch_number:>03d}{financial_year:>04d}{name:<200.200s}{trading_name:<200.200s}" \
    "{postal_address1:<38.38s}{postal_address2:<38.38s}{postal_suburb:<27.27s}{postal_state:<3.3s}{postal_postcode:>04d}{postal_country:<20.20s}" \
    "{contact_name:<38.38s}{telephone_number:<15.15s}{fax_number:<15.15s}{empty:1.1s}"
          
SOFTWARE_DATA_RECORD = "628SOFTWARE{type_and_developer:<80.80s}N{empty:536.536s}"

INDIVIDUAL_NON_BUSINESS_PAYMENT_SUMMARY_RECORD = "628DINB{income_type:<1.1s}{tax_file_number:>09d}{birth_date:<8.8s}{surname:<30.30s}{given_name1:<15.15s}{given_name2:<15.15s}" \
    "{street_address1:<38.38s}{street_address2:<38.38s}{street_suburb:<27.27s}{street_state:<3.3s}{street_postcode:>04d}{street_country:<20.20s}" \
    "{start_date:<8.8s}{end_date:<8.8s}"\
    "{tax_withheld:>08d}{gross_payments:>08d}{allowances:>08d}{lump_sumA:>08d}{lump_sumB:>08d}{lump_sumD:>08d}{lump_sumE:>08d}{community_development:>08d}00000000{reportable_fringe_benefits:>08d}"\
    "{amendment:<1.1s}{reportable_super:>08d}{lump_sumA_type:<1.1s}{workplace_giving:>08d}{union:>08d}{exempt_foreign:>08d}{annuity_deductible:>08d}{empty:275.275s}"
    
FILE_TOTAL_RECORD = "628FILE-TOTAL{number_of_records:>08d}{empty:607.607s}"

class PaygSummaryEncoder:   
    def encode(self, data, fp):
      self.fp = fp
      self.number_of_records = 0
      
      data['supplier']['run_type'] = 'P' # P = Production, T = Test
      # supplier.fax_number is optional
      # supplier.file_reference is optional
      # supplier.email is optional
      
      # Supplier data records
      self._writerow(SUPPLIER_DATA_RECORD1.format(empty='', **data['supplier']))
      self._writerow(SUPPLIER_DATA_RECORD2.format(empty='', **data['supplier']))
      self._writerow(SUPPLIER_DATA_RECORD3.format(empty='', **data['supplier']))

      
      # (Repeated) Payer identity
      for payer in data['payer']:          
          # payer.trading_name optional
          # payer.contact_name optional
          # payer.telephone_number optional
          # payer.fax_number optional
          self._writerow(PAYER_IDENTITY_RECORD.format(empty='', **payer))
          
          # Software data record
          self._writerow(SOFTWARE_DATA_RECORD.format(empty='', type_and_developer="INHOUSEusableefficiency"))
          
          # (Repeated) Individual non-business payment summary data record
          for payee in payer['individual']:
            # given_name2 is optional
            self._writerow(INDIVIDUAL_NON_BUSINESS_PAYMENT_SUMMARY_RECORD.format(empty='', **payee))
          
          # Don't think I need these next two but need to check
          # (Repeated) Business and personal services income payment summary data record?
          # (Repeated) Superannuation income stream payment summary data record?
          
      # File total
      self._writerow(FILE_TOTAL_RECORD.format(empty='', number_of_records=self.number_of_records+1))
          
    def _writerow(self, row):
        if len(row) != 628:
            raise Exception("Length is actually %d, stripped %d: %s"%(len(row), len(row.rstrip()), row))
        self.number_of_records+=1
        self.fp.write(row+"\r\n")

if __name__ == "__main__":
    encoder = PaygSummaryEncoder()
    payg_information = json.load(open(sys.argv[1], 'r'))  
    output_file = open(sys.argv[2], "w")
    encoder.encode(payg_information, output_file)
