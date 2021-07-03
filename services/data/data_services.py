import os

from flask import flash, request, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse
from werkzeug.utils import secure_filename
import pandas as pd
from resource.models import CompanyModel, CompanyDailyModel, CompanyHourlyModel
from datetime import datetime

parser = reqparse.RequestParser()
ALLOWED_EXTENSIONS = {'csv'}
UPLOAD_FOLDER = 'data/uploads'


class DataInsert(Resource):

    def allowed_file(self, filename: str):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def store_data_to_DB(self, file_path):
        bulk_df = pd.read_csv(file_path)
        bulk_df = bulk_df[['Company ID', 'Company Name', 'Creation Date', 'Total']]

        # store the company to db if it does not exists
        unique_companies = bulk_df.drop_duplicates(subset=["Company ID"])
        for _, row in unique_companies.iterrows():
            if CompanyModel.find_by_branch_number(row['Company ID']):
                pass
            else:
                new_company = CompanyModel(
                    branch_number=row['Company ID'],
                    company_name=row['Company Name']
                )
                new_company.save_to_db()
        x = 0
        # store the company daily to db if it does not exists
        for _, row in bulk_df.iterrows():
            company_id = CompanyModel.find_by_branch_number(row['Company ID']).id
            date = row['Creation Date'].split(' ')[0]
            total = float(row['Total'])
            company_daily = CompanyDailyModel.find_by_company_id_and_date(company_id, date)
            if company_daily:
                CompanyDailyModel.update_company_daily(company_daily.id, total)
            else:
                new_company_daily = CompanyDailyModel(
                    company_id=company_id,
                    date=date,
                    total=total
                )
                new_company_daily.save_to_db()

            company_daily_id = CompanyDailyModel.find_by_company_id_and_date(company_id, date).id
            hour = row['Creation Date'].split(' ')[1]

            new_company_hourly = CompanyHourlyModel(
                company_daily_id=company_daily_id,
                hour=hour,
                total=total
            )
            new_company_hourly.save_to_db()

    @jwt_required()
    def post(self):
        data = parser.parse_args()
        token = get_jwt_identity()
        if token["group"] == "admin":
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return {'message': 'file does not exist'}
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and self.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                self.store_data_to_DB(os.path.join(os.path.join(UPLOAD_FOLDER, filename)))

                return {'message': 'file uploaded'}
            else:
                return {'message': 'file format does not supported'}
        else:
            return {'message': 'you have not access to this api'}


# ---------------------------------------------------------------------------
class DailyQuery(Resource):
    parser.add_argument('branch_id', help='This field cannot be blank')
    parser.add_argument('start', help='This field cannot be blank')
    parser.add_argument('end', help='This field cannot be blank')

    @jwt_required()
    def get(self):
        data = parser.parse_args()
        token = get_jwt_identity()
        company = CompanyModel.find_by_branch_number(data['branch_id'])
        start_company_daily_date_time_obj = datetime.strptime(data['start'], '%Y-%m-%d').date()
        end_company_daily_date_time_obj = datetime.strptime(data['end'], '%Y-%m-%d').date()

        results = dict()
        if company:
            company_dailies = CompanyDailyModel.find_by_company_id(company.id)
            if company_dailies:
                for company_daily in company_dailies:
                    db_company_daily_date_time_obj = datetime.strptime(company_daily.date, '%d/%m/%y').date()
                    if start_company_daily_date_time_obj <= db_company_daily_date_time_obj <= end_company_daily_date_time_obj:
                        results[str(db_company_daily_date_time_obj)] = "%.2f" %float(company_daily.total)
            else:
                return {'message': 'this company does not have any transaction'}
        else:
            return {'message': 'company branch does not exist'}

        total = 0
        for _, value in results.items():
            total += float(value)
        results['total'] = "%.2f" %total

        return results


# ---------------------------------------------------------------------------
class HourlyQuery(Resource):
    parser.add_argument('branch_id', help='This field cannot be blank')
    parser.add_argument('date', help='This field cannot be blank')
    parser.add_argument('start hour', help='This field cannot be blank')
    parser.add_argument('end hour', help='This field cannot be blank')

    @jwt_required()
    def get(self):
        data = parser.parse_args()
        token = get_jwt_identity()
        company = CompanyModel.find_by_branch_number(data['branch_id'])
        date_time_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
        start_company_time_obj = datetime.strptime(data['start hour'], '%H:%M').time()
        end_company_time_obj = datetime.strptime(data['end hour'], '%H:%M').time()

        results = dict()
        if company:
            company_daily = CompanyDailyModel.find_by_company_id_and_date(company.id,
                                                                          date_time_obj.strftime('%d/%m/%y'))
            if company_daily:
                company_hourlies = CompanyHourlyModel.find_by_company_daily_id(company_daily.id)
                for company_hourly in company_hourlies:
                    db_company_hourly_date_time_obj = datetime.strptime(company_hourly.hour, '%H:%M').time()
                    if start_company_time_obj <= db_company_hourly_date_time_obj <= end_company_time_obj:
                        if company_hourly.hour in results:
                            results[company_hourly.hour] += float("%.2f" %company_hourly.total)
                        else:
                            results[company_hourly.hour] = float("%.2f" %company_hourly.total)

            else:
                return {'message': 'this company does not have any transaction at given date'}
        else:
            return {'message': 'company branch does not exist'}
        total = 0
        for _, value in results.items():
            total += float(value)
        results['total'] = "%.2f" %total

        return results
# ---------------------------------------------------------------------------
