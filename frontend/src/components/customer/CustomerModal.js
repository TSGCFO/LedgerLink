import React from 'react';
import { Dialog, DialogTitle, DialogContent, TextField, Button, DialogActions, FormControlLabel, Radio, RadioGroup } from '@mui/material';
import { Formik, Form, Field, FieldArray, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import axios from 'axios';

const customerSchema = Yup.object().shape({
  customerId: Yup.number().required('Customer ID is required').typeError('Customer ID must be a number'),
  companyName: Yup.string().matches(/^[\w\s\-,.()]+$/, 'Invalid characters').required('Company name is required'),
  legalBusinessName: Yup.string().matches(/^[\w\s\-,.()]+$/, 'Invalid characters').required('Legal business name is required'),
  email: Yup.string().email('Invalid email'),
  phone: Yup.string(),
  address: Yup.string(),
  city: Yup.string(),
  state: Yup.string(),
  zip: Yup.string(),
  country: Yup.string(),
  accountsPayable: Yup.array().of(
    Yup.object().shape({
      name: Yup.string(),
      email: Yup.string().email('Invalid email'),
      phone: Yup.string(),
    })
  ),
  businessType: Yup.string()
});

const CustomerModal = ({ open, handleClose }) => {
  return (
    <Dialog open={open} onClose={handleClose}>
      <DialogTitle>Create Customer</DialogTitle>
      <Formik
        initialValues={{
          customerId: '',
          companyName: '',
          legalBusinessName: '',
          email: '',
          phone: '',
          address: '',
          city: '',
          state: '',
          zip: '',
          country: '',
          accountsPayable: [{ name: '', email: '', phone: '' }],
          businessType: ''
        }}
        validationSchema={customerSchema}
        onSubmit={(values, { setSubmitting }) => {
          axios.post('http://localhost:5000/customers', values)
            .then(response => {
              console.log(response.data);
              setSubmitting(false);
              alert('Customer created successfully'); // User feedback
              handleClose();
            })
            .catch(error => {
              console.error('There was an error!', error);
              alert('Failed to create customer.'); // User feedback for errors
              setSubmitting(false);
            });
        }}
      >
        {formikProps => (
          <Form>
            <DialogContent>
              <Field as={TextField} name="customerId" label="Customer ID" fullWidth />
              <ErrorMessage name="customerId" component="div" style={{ color: 'red' }} />
              <Field as={TextField} name="companyName" label="Company Name" fullWidth />
              <ErrorMessage name="companyName" component="div" style={{ color: 'red' }} />
              <Field as={TextField} name="legalBusinessName" label="Legal Business Name" fullWidth />
              <ErrorMessage name="legalBusinessName" component="div" style={{ color: 'red' }} />
              <Field as={TextField} name="email" label="Email" fullWidth />
              <ErrorMessage name="email" component="div" style={{ color: 'red' }} />
              <Field as={TextField} name="phone" label="Phone" fullWidth />
              <ErrorMessage name="phone" component="div" style={{ color: 'red' }} />
              <Field as={TextField} name="address" label="Address" fullWidth />
              <ErrorMessage name="address" component="div" style={{ color: 'red' }} />
              <Field as={TextField} name="city" label="City" fullWidth />
              <ErrorMessage name="city" component="div" style={{ color: 'red' }} />
              <Field as={TextField} name="state" label="State" fullWidth />
              <ErrorMessage name="state" component="div" style={{ color: 'red' }} />
              <Field as={TextField} name="zip" label="Zip" fullWidth />
              <ErrorMessage name="zip" component="div" style={{ color: 'red' }} />
              <Field as={TextField} name="country" label="Country" fullWidth />
              <ErrorMessage name="country" component="div" style={{ color: 'red' }} />
              <FieldArray name="accountsPayable">
                {({ push, remove }) => (
                  formikProps.values.accountsPayable.map((account, index) => (
                    <div key={index}>
                      <Field as={TextField} name={`accountsPayable.${index}.name`} label="Name" fullWidth />
                      <ErrorMessage name={`accountsPayable.${index}.name`} component="div" style={{ color: 'red' }} />
                      <Field as={TextField} name={`accountsPayable.${index}.email`} label="Email" fullWidth />
                      <ErrorMessage name={`accountsPayable.${index}.email`} component="div" style={{ color: 'red' }} />
                      <Field as={TextField} name={`accountsPayable.${index}.phone`} label="Phone" fullWidth />
                      <ErrorMessage name={`accountsPayable.${index}.phone`} component="div" style={{ color: 'red' }} />
                      <Button type="button" onClick={() => remove(index)}>Remove</Button>
                      {index === formikProps.values.accountsPayable.length - 1 && (
                        <Button type="button" onClick={() => push({ name: '', email: '', phone: '' })}>Add More</Button>
                      )}
                    </div>
                  ))
                )}
              </FieldArray>
              <RadioGroup name="businessType">
                <FormControlLabel value="Sole Proprietorship" control={<Radio />} label="Sole Proprietorship" />
                <FormControlLabel value="Partnership" control={<Radio />} label="Partnership" />
                <FormControlLabel value="Corporation" control={<Radio />} label="Corporation" />
                <FormControlLabel value="LLC" control={<Radio />} label="LLC" />
                <FormControlLabel value="Non-Profit" control={<Radio />} label="Non-Profit" />
                <FormControlLabel value="Other" control={<Radio />} label="Other" />
              </RadioGroup>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleClose}>Cancel</Button>
              <Button type="submit" color="primary">Save and Close</Button>
            </DialogActions>
          </Form>
        )}
      </Formik>
    </Dialog>
  );
};

export default CustomerModal;