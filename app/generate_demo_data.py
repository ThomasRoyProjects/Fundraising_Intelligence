import pandas as pd
import random
from datetime import datetime, timedelta

rows = 6000

headers = """nationbuilder_id	type	amount	amount_in_cents	election_cycle	election_period_ngp_code	election_period_name	election_period_id	payment_type_ngp_code	payment_type_name	payment_type_id	check_number	created_at	recruiter_id	recruiter_name	tracking_code_slug	authorization	transaction_key	ngp_id	actblue_order_number	fec_type_ngp_code	fec_type_name	fec_type_id	succeeded_at	failed_at	canceled_at	is_private	ip_address	note	is_corporate_contribution	page_slug	parent_transaction_id	recurring_donation_status	merchant_account_name	billing_address1	billing_address2	billing_address3	billing_city	billing_state	billing_zip	billing_country	billing_country_code	billing_county	billing_fips	billing_submitted_address	work_address1	work_address2	work_address3	work_city	work_state	work_zip	work_country	work_country_code	work_county	work_fips	work_submitted_address	posting_date	finance_type_name	finance_type_id	is_transfer	support_status	supported_or_opposed_name	reporting_description	invoice_name	invoice_company	reference	amount_paid	amount_paid_in_cents	days_to_pay	sent_at	closed_at	start_at	end_at	percent_discount	amount_discount	amount_discount_in_cents	amount_subsidized	amount_subsidized_in_cents	amount_with_discount	amount_with_discount_in_cents	point_person_id	point_person_name	signup_nationbuilder_id	signup_twitter_id	signup_twitter_login	signup_facebook_username	signup_meetup_id	signup_civicrm_id	signup_external_id	signup_salesforce_id	signup_prefix	signup_first_name	signup_middle_name	signup_last_name	signup_suffix	signup_full_name	signup_legal_name	signup_employer	signup_occupation	signup_sex	signup_party	signup_religion	signup_church	signup_ethnicity	signup_marital_status	signup_website	signup_language	signup_is_deceased	signup_born_at	signup_email	signup_email1	signup_email2	signup_email3	signup_email4	signup_email_opt_in	signup_phone_number	signup_work_phone_number	signup_do_not_call	signup_do_not_contact	signup_federal_donotcall	signup_mobile_number	signup_mobile_opt_in	signup_is_mobile_bad	signup_fax_number	signup_demo	signup_support_level	signup_inferred_support_level	signup_priority_level	signup_availability	signup_note	signup_parent_id	signup_point_person_name_or_email	signup_recruiter_id	signup_recruiter_name_or_email	signup_tag_list	signup_created_at	signup_unsubscribed_at	signup_is_supporter	signup_is_prospect	signup_signup_type	signup_is_volunteer	signup_is_donor	signup_is_fundraiser	signup_is_ignore_donation_limits	signup_first_donated_at	signup_last_donated_at	signup_donations_count	signup_donations_amount	signup_donations_amount_in_cents	signup_donations_raised_count	signup_donations_raised_amount	signup_donations_raised_amount_in_cents	signup_donations_pledged_amount	signup_donations_pledged_amount_in_cents	signup_donations_count_this_cycle	signup_donations_amount_this_cycle	signup_donations_amount_this_cycle_in_cents	signup_donations_raised_count_this_cycle	signup_donations_raised_amount_this_cycle	signup_donations_raised_amount_this_cycle_in_cents	signup_maximum_donation_possible_this_cycle	signup_maximum_donation_possible_this_cycle_in_cents	signup_is_customer	signup_first_invoice_at	signup_last_invoice_at	signup_active_customer_started_at	signup_active_customer_expires_at	signup_invoices_count	signup_closed_invoices_count	signup_outstanding_invoices_count	signup_invoices_amount_in_cents	signup_invoices_amount	signup_closed_invoices_amount_in_cents	signup_closed_invoices_amount	signup_outstanding_invoices_amount_in_cents	signup_outstanding_invoices_amount	signup_invoice_payments_amount_in_cents	signup_invoice_payments_amount	signup_invoice_payments_referred_amount	signup_invoice_payments_referred_amount_in_cents	signup_membership_names	signup_memberships_started_at	signup_memberships_expires_on	signup_memberships_suspended_at	signup_nbec_guid	signup_pf_strat_id	signup_state_file_id	signup_county_file_id	signup_dw_id	signup_van_id	signup_ngp_id	signup_rnc_id	signup_rnc_regid	signup_datatrust_id	signup_previous_party	signup_inferred_party	signup_supranational_district	signup_federal_district	signup_state_upper_district	signup_state_lower_district	signup_county_district	signup_city_district	signup_city_sub_district	signup_village_district	signup_judicial_district	signup_school_district	signup_school_sub_district	signup_fire_district	signup_precinct_name	signup_precinct_code	signup_media_market_name	signup_support_probability_score	signup_turnout_probability_score	signup_capital_amount	signup_capital_amount_in_cents	signup_spent_capital_amount	signup_spent_capital_amount_in_cents	signup_received_capital_amount	signup_received_capital_amount_in_cents	signup_billing_address1	signup_billing_address2	signup_billing_address3	signup_billing_city	signup_billing_state	signup_billing_zip	signup_billing_country	signup_billing_country_code	signup_billing_county	signup_billing_fips	signup_billing_submitted_address	signup_cpchq_do_not_call	signup_cpchq_do_not_mail	signup_cpchq_do_not_email	signup_lifetime_donations_total	signup_lawnsign_yn	payout_id	soft_credit_recipient_ids	soft_credit_recipient_names""".split("\t")

start_date = datetime(2024,1,1)
end_date = datetime.now()

first_names = [
"Liam","Noah","Oliver","Elijah","James","William","Benjamin","Lucas","Henry","Alexander",
"Mason","Michael","Ethan","Daniel","Jacob","Logan","Jackson","Levi","Sebastian","Mateo",
"Jack","Owen","Theodore","Aiden","Samuel","Joseph","John","David","Wyatt","Matthew",
"Luke","Asher","Carter","Julian","Grayson","Leo","Jayden","Gabriel","Isaac","Lincoln",
"Anthony","Hudson","Dylan","Ezra","Thomas","Charles","Christopher","Jaxon","Maverick","Josiah",
"Isaiah","Andrew","Elias","Joshua","Nathan","Caleb","Ryan","Adrian","Miles","Eli",
"Nolan","Christian","Aaron","Cameron","Ezekiel","Colton","Luca","Landon","Hunter","Jonathan",
"Santiago","Axel","Easton","Cooper","Jeremiah","Angel","Roman","Connor","Jameson","Robert",
"Greyson","Jordan","Ian","Carson","Jaxson","Leonardo","Dominic","Austin","Everett","Brooks",
"Xavier","Kai","Jose","Parker","Adam","Jace","Wesley","Kayden","Silas","Declan",
"Theo","Finn","Rowan","Bennett","Ryder","Atlas","Archer","Beckett","Emmett","Felix",
"Gavin","Harrison","Jasper","Kieran","Malcolm","Nico","Orion","Paxton","Quentin","Reid",
"Spencer","Tucker","Vincent","Walker","Zachary","Brandon","Colby","Damian","Elliot","Frank",
"Garrett","Harvey","Ivan","Jared","Keegan","Leland","Marcus","Neil","Oscar","Preston",
"Quincy","Ronan","Sterling","Trevor","Ulrich","Victor","Warren","Xander","Yusuf","Zane",
"Abraham","Bryce","Clayton","Derek","Edgar","Frederick","Gordon","Hugh","Irwin","Jerome",
"Kyle","Lawrence","Mitchell","Nathaniel","Otto","Philip","Randall","Shawn","Terrence","Vernon",
"Wes","Yahir","Zeke","Andre","Brett","Curtis","Darren","Emanuel","Forrest","Grant",
"Heath","Ira","Jonah","Kurt","Luther","Martin","Noel","Omar","Pierce","Ralph",
"Saul","Trent","Ulysses","Vaughn","Wayne","Xzavier","Yosef","Zion"
]
last_names = [
"Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
"Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
"Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson",
"Walker","Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
"Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell","Carter","Roberts",
"Gomez","Phillips","Evans","Turner","Diaz","Parker","Cruz","Edwards","Collins","Reyes",
"Stewart","Morris","Morales","Murphy","Cook","Rogers","Gutierrez","Ortiz","Morgan","Cooper",
"Peterson","Bailey","Reed","Kelly","Howard","Ramos","Kim","Cox","Ward","Richardson",
"Watson","Brooks","Chavez","Wood","James","Bennett","Gray","Mendoza","Ruiz","Hughes",
"Price","Alvarez","Castillo","Sanders","Patel","Myers","Long","Ross","Foster","Jimenez",
"Stephens","Fleming","Holland","Bishop","Carr","Douglas","Ellis","Franklin","Griffin",
"Hawkins","Johnston","Kelley","Larsen","Marshall","Nicholson","Owens","Porter","Quinn","Ramsey",
"Schneider","Sullivan","Terry","Underwood","Vargas","Wade","Yates","Zimmerman","Andrade","Boone",
"Cannon","Dalton","Estes","Figueroa","Gallegos","Huffman","Ingram","Jarvis","Kramer","Landry",
"Macdonald","Nash","Olsen","Pruitt","Qualls","Rivas","Salazar","Talley","Upton","Valdez",
"Wagner","Xiong","Ybarra","Zamora","Arnold","Barrett","Caldwell","Delgado","Espinoza","Farrell",
"Garrison","Holloway","Irving","Jennings","Knox","Lowe","McBride","Norton","Owens","Phelps",
"Quintero","Rocha","Serrano","Tate","Usher","Velez","Wilcox","York","Zuniga","Bradford",
"Chandler","Donovan","Everett","Fischer","Gallagher","Hancock","Iverson","Jefferson","Keller","Lambert",
"Montoya","Nielsen","Osborne","Patterson","Quade","Ritter","Shepard","Thornton","Uribe","Vance"
]
donor_pool_size = 1200
donor_pool = []

for i in range(donor_pool_size):

    first = random.choice(first_names)
    last = random.choice(last_names)

    donor_type = random.choices(
        ["local_loyal","hq_recurring","mixed"],
        weights=[0.45,0.30,0.25]
    )[0]

    donor_pool.append({
        "id": i + 1,
        "first": first,
        "last": last,
        "email": f"{first.lower()}.{last.lower()}{i}@example.com",
        "type": donor_type
    })

data = []

for i in range(rows):

    donor = random.choice(donor_pool)

    name = donor["first"]
    last = donor["last"]
    email = donor["email"]
    person_id = donor["id"]

    amount = random.choices(
        [5,10,15,20,25,35,50,75,100,150,250,500,750,1000],
        weights=[18,16,14,12,10,8,7,6,4,3,1,1,0.5,0.5]
    )[0]

    cents = amount * 100

    donor_type = donor["type"]

    if donor_type == "local_loyal":

        tracking = random.choices(
            ["local_party","tickets"],
            weights=[0.85,0.15]
        )[0]

    elif donor_type == "hq_recurring":

        tracking = "national_party"

    else:

        tracking = random.choice(
            ["local_party","national_party"]
        )

    if donor_type == "hq_recurring" and random.random() < 0.65:

        months_back = random.randint(0,18)
        random_date = datetime.now() - timedelta(days=30*months_back)

    else:

        random_date = start_date + timedelta(
            seconds=random.randint(0,int((end_date-start_date).total_seconds()))
        )

    base = {
        "nationbuilder_id": i + 1,
        "signup_nationbuilder_id": person_id,
        "type": "Donation",
        "amount": amount,
        "amount_in_cents": cents,
        "tracking_code_slug": tracking,
        "signup_first_name": name,
        "signup_last_name": last,
        "signup_full_name": f"{name} {last}",
        "signup_email": email,
        "signup_phone_number": f"250555{random.randint(1000,9999)}",
        "billing_city": "Victoria",
        "billing_state": "BC",
        "billing_country": "Canada",
        "succeeded_at": random_date.strftime("%m/%d/%Y %I:%M %p"),
        "amount_paid": amount,
        "amount_paid_in_cents": cents
    }

    row = {h: base.get(h,"") for h in headers}
    data.append(row)

df = pd.DataFrame(data, columns=headers)

df.to_csv("fake_nationbuilder_transactions.csv", index=False)

print("Generated fake_nationbuilder_transactions.csv with 6000 rows")