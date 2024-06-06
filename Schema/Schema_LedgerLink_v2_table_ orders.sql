--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3
-- Dumped by pg_dump version 16.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    transaction_id integer NOT NULL,
    create_date timestamp without time zone NOT NULL,
    customer_id integer NOT NULL,
    customer_name character varying(100) NOT NULL,
    close_date timestamp without time zone,
    reference_number character varying(50) NOT NULL,
    ship_to_name character varying(100) NOT NULL,
    ship_to_company character varying(100),
    ship_to_address character varying(200) NOT NULL,
    ship_to_address2 character varying(200),
    ship_to_city character varying(100) NOT NULL,
    ship_to_state character varying(50) NOT NULL,
    ship_to_zip character varying(20) NOT NULL,
    ship_to_country character varying(50) NOT NULL,
    carrier character varying(100),
    total_weight_lb numeric(10,2),
    line_items integer,
    sku_quantity jsonb,
    total_item_qty integer,
    volume_cuft numeric(10,2),
    packages integer,
    markfor_lists text,
    ship_service character varying(100),
    warehouse_instructions text,
    allocation_status character varying(50),
    asn_sent_date timestamp without time zone,
    batch_id character varying(50),
    batch_name character varying(100),
    bill_of_lading character varying(100),
    billing_type character varying(50),
    cancel_date timestamp without time zone,
    confirm_asn_sent_date timestamp without time zone,
    earliest_ship_date timestamp without time zone,
    end_of_day_request_date timestamp without time zone,
    load_number character varying(50),
    load_out_percent numeric(5,2),
    load_out_date timestamp without time zone,
    markfor_name_id character varying(100),
    master_bill_of_lading character varying(100),
    pack_done_date timestamp without time zone,
    parcel_label_type character varying(50),
    pick_done_date timestamp without time zone,
    pick_job_assignee character varying(50),
    pick_job_id character varying(50),
    pick_ticket_print_date timestamp without time zone,
    pickup_date timestamp without time zone,
    purchase_order character varying(100),
    retailer_id character varying(50),
    ship_to_email character varying(100),
    ship_to_phone character varying(20),
    small_parcel_ship_date timestamp without time zone,
    status character varying(50),
    time_zone character varying(50),
    tracking_number character varying(100),
    volume_m3 numeric(10,2),
    warehouse character varying(100),
    total_weight_kg numeric(10,2),
    created_by character varying(50),
    updated_by character varying(50),
    create_source character varying(50),
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT orders_line_items_check CHECK ((line_items >= 0)),
    CONSTRAINT orders_load_out_percent_check CHECK (((load_out_percent >= (0)::numeric) AND (load_out_percent <= (100)::numeric))),
    CONSTRAINT orders_packages_check CHECK ((packages >= 0)),
    CONSTRAINT orders_total_item_qty_check CHECK ((total_item_qty >= 0)),
    CONSTRAINT orders_total_weight_kg_check CHECK ((total_weight_kg >= (0)::numeric)),
    CONSTRAINT orders_total_weight_lb_check CHECK ((total_weight_lb >= (0)::numeric)),
    CONSTRAINT orders_volume_cuft_check CHECK ((volume_cuft >= (0)::numeric)),
    CONSTRAINT orders_volume_m3_check CHECK ((volume_m3 >= (0)::numeric))
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (transaction_id);


--
-- Name: idx_orders_create_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_create_date ON public.orders USING btree (create_date);


--
-- Name: idx_orders_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_customer_id ON public.orders USING btree (customer_id);


--
-- Name: idx_orders_reference_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_reference_number ON public.orders USING btree (reference_number);


--
-- Name: idx_orders_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_status ON public.orders USING btree (status);


--
-- Name: idx_orders_tracking_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_tracking_number ON public.orders USING btree (tracking_number);


--
-- Name: idx_orders_transaction_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_transaction_id ON public.orders USING btree (transaction_id);


--
-- Name: orders update_orders_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON public.orders FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: orders orders_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(customer_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

