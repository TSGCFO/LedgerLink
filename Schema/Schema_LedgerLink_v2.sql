--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3
-- Dumped by pg_dump version 16.3

-- Started on 2024-06-04 22:50:51

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

--
-- TOC entry 5 (class 2615 OID 32827)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- TOC entry 248 (class 1255 OID 36020)
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 244 (class 1259 OID 34138)
-- Name: customer_services; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer_services (
    customer_service_id integer NOT NULL,
    customer_id integer NOT NULL,
    service_id integer NOT NULL,
    unit_price numeric(10,2) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.customer_services OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 34137)
-- Name: customer_services_customer_service_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customer_services_customer_service_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customer_services_customer_service_id_seq OWNER TO postgres;

--
-- TOC entry 5283 (class 0 OID 0)
-- Dependencies: 243
-- Name: customer_services_customer_service_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customer_services_customer_service_id_seq OWNED BY public.customer_services.customer_service_id;


--
-- TOC entry 217 (class 1259 OID 33674)
-- Name: customers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customers (
    customer_id integer NOT NULL,
    company_name character varying(100) NOT NULL,
    legal_business_name character varying(100) NOT NULL,
    email character varying(100),
    phone character varying(20),
    address character varying(200),
    city character varying(50),
    state character varying(50),
    zip character varying(20),
    country character varying(50),
    business_type character varying(50),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.customers OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 32840)
-- Name: customers_customer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customers_customer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customers_customer_id_seq OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 33673)
-- Name: customers_customer_id_seq1; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customers_customer_id_seq1
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.customers_customer_id_seq1 OWNER TO postgres;

--
-- TOC entry 5284 (class 0 OID 0)
-- Dependencies: 216
-- Name: customers_customer_id_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customers_customer_id_seq1 OWNED BY public.customers.customer_id;


--
-- TOC entry 240 (class 1259 OID 34005)
-- Name: inserts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inserts (
    insert_id integer NOT NULL,
    sku character varying(100),
    customer_id integer,
    insert_name character varying(100) NOT NULL,
    insert_quantity integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT inserts_insert_quantity_check CHECK ((insert_quantity >= 0))
);


ALTER TABLE public.inserts OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 34004)
-- Name: inserts_insert_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inserts_insert_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inserts_insert_id_seq OWNER TO postgres;

--
-- TOC entry 5285 (class 0 OID 0)
-- Dependencies: 239
-- Name: inserts_insert_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inserts_insert_id_seq OWNED BY public.inserts.insert_id;


--
-- TOC entry 247 (class 1259 OID 35993)
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
-- TOC entry 218 (class 1259 OID 33686)
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
)
PARTITION BY HASH (customer_id);


ALTER TABLE public.products OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 33703)
-- Name: products_partition_0; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_0 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_0 OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 33718)
-- Name: products_partition_1; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_1 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_1 OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 33853)
-- Name: products_partition_10; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_10 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_10 OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 33868)
-- Name: products_partition_11; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_11 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_11 OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 33883)
-- Name: products_partition_12; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_12 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_12 OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 33898)
-- Name: products_partition_13; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_13 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_13 OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 33913)
-- Name: products_partition_14; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_14 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_14 OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 33928)
-- Name: products_partition_15; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_15 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_15 OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 33943)
-- Name: products_partition_16; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_16 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_16 OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 33958)
-- Name: products_partition_17; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_17 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_17 OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 33973)
-- Name: products_partition_18; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_18 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_18 OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 33988)
-- Name: products_partition_19; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_19 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_19 OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 33733)
-- Name: products_partition_2; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_2 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_2 OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 33748)
-- Name: products_partition_3; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_3 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_3 OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 33763)
-- Name: products_partition_4; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_4 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_4 OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 33778)
-- Name: products_partition_5; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_5 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_5 OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 33793)
-- Name: products_partition_6; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_6 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_6 OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 33808)
-- Name: products_partition_7; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_7 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_7 OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 33823)
-- Name: products_partition_8; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_8 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_8 OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 33838)
-- Name: products_partition_9; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_partition_9 (
    sku character varying(100) NOT NULL,
    customer_id integer NOT NULL,
    labeling_unit_1 character varying(50),
    labeling_quantity_1 integer,
    labeling_unit_2 character varying(50),
    labeling_quantity_2 integer,
    labeling_unit_3 character varying(50),
    labeling_quantity_3 integer,
    labeling_unit_4 character varying(50),
    labeling_quantity_4 integer,
    labeling_unit_5 character varying(50),
    labeling_quantity_5 integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT products_labeling_quantity_1_check CHECK ((labeling_quantity_1 >= 0)),
    CONSTRAINT products_labeling_quantity_2_check CHECK ((labeling_quantity_2 >= 0)),
    CONSTRAINT products_labeling_quantity_3_check CHECK ((labeling_quantity_3 >= 0)),
    CONSTRAINT products_labeling_quantity_4_check CHECK ((labeling_quantity_4 >= 0)),
    CONSTRAINT products_labeling_quantity_5_check CHECK ((labeling_quantity_5 >= 0))
);


ALTER TABLE public.products_partition_9 OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 34159)
-- Name: service_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.service_logs (
    log_id integer NOT NULL,
    customer_id integer NOT NULL,
    sku character varying(100) NOT NULL,
    service_id integer NOT NULL,
    quantity integer NOT NULL,
    total_cost numeric(10,2) NOT NULL,
    performed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT service_logs_quantity_check CHECK ((quantity >= 0))
);


ALTER TABLE public.service_logs OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 34158)
-- Name: service_logs_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.service_logs_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_logs_log_id_seq OWNER TO postgres;

--
-- TOC entry 5286 (class 0 OID 0)
-- Dependencies: 245
-- Name: service_logs_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.service_logs_log_id_seq OWNED BY public.service_logs.log_id;


--
-- TOC entry 242 (class 1259 OID 34124)
-- Name: services; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.services (
    service_id integer NOT NULL,
    service_name character varying(100) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.services OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 34123)
-- Name: services_service_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.services_service_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.services_service_id_seq OWNER TO postgres;

--
-- TOC entry 5287 (class 0 OID 0)
-- Dependencies: 241
-- Name: services_service_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.services_service_id_seq OWNED BY public.services.service_id;


--
-- TOC entry 4798 (class 0 OID 0)
-- Name: products_partition_0; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_0 FOR VALUES WITH (modulus 20, remainder 0);


--
-- TOC entry 4799 (class 0 OID 0)
-- Name: products_partition_1; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_1 FOR VALUES WITH (modulus 20, remainder 1);


--
-- TOC entry 4808 (class 0 OID 0)
-- Name: products_partition_10; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_10 FOR VALUES WITH (modulus 20, remainder 10);


--
-- TOC entry 4809 (class 0 OID 0)
-- Name: products_partition_11; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_11 FOR VALUES WITH (modulus 20, remainder 11);


--
-- TOC entry 4810 (class 0 OID 0)
-- Name: products_partition_12; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_12 FOR VALUES WITH (modulus 20, remainder 12);


--
-- TOC entry 4811 (class 0 OID 0)
-- Name: products_partition_13; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_13 FOR VALUES WITH (modulus 20, remainder 13);


--
-- TOC entry 4812 (class 0 OID 0)
-- Name: products_partition_14; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_14 FOR VALUES WITH (modulus 20, remainder 14);


--
-- TOC entry 4813 (class 0 OID 0)
-- Name: products_partition_15; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_15 FOR VALUES WITH (modulus 20, remainder 15);


--
-- TOC entry 4814 (class 0 OID 0)
-- Name: products_partition_16; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_16 FOR VALUES WITH (modulus 20, remainder 16);


--
-- TOC entry 4815 (class 0 OID 0)
-- Name: products_partition_17; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_17 FOR VALUES WITH (modulus 20, remainder 17);


--
-- TOC entry 4816 (class 0 OID 0)
-- Name: products_partition_18; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_18 FOR VALUES WITH (modulus 20, remainder 18);


--
-- TOC entry 4817 (class 0 OID 0)
-- Name: products_partition_19; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_19 FOR VALUES WITH (modulus 20, remainder 19);


--
-- TOC entry 4800 (class 0 OID 0)
-- Name: products_partition_2; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_2 FOR VALUES WITH (modulus 20, remainder 2);


--
-- TOC entry 4801 (class 0 OID 0)
-- Name: products_partition_3; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_3 FOR VALUES WITH (modulus 20, remainder 3);


--
-- TOC entry 4802 (class 0 OID 0)
-- Name: products_partition_4; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_4 FOR VALUES WITH (modulus 20, remainder 4);


--
-- TOC entry 4803 (class 0 OID 0)
-- Name: products_partition_5; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_5 FOR VALUES WITH (modulus 20, remainder 5);


--
-- TOC entry 4804 (class 0 OID 0)
-- Name: products_partition_6; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_6 FOR VALUES WITH (modulus 20, remainder 6);


--
-- TOC entry 4805 (class 0 OID 0)
-- Name: products_partition_7; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_7 FOR VALUES WITH (modulus 20, remainder 7);


--
-- TOC entry 4806 (class 0 OID 0)
-- Name: products_partition_8; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_8 FOR VALUES WITH (modulus 20, remainder 8);


--
-- TOC entry 4807 (class 0 OID 0)
-- Name: products_partition_9; Type: TABLE ATTACH; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ATTACH PARTITION public.products_partition_9 FOR VALUES WITH (modulus 20, remainder 9);


--
-- TOC entry 4869 (class 2604 OID 34141)
-- Name: customer_services customer_service_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_services ALTER COLUMN customer_service_id SET DEFAULT nextval('public.customer_services_customer_service_id_seq'::regclass);


--
-- TOC entry 4818 (class 2604 OID 33677)
-- Name: customers customer_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers ALTER COLUMN customer_id SET DEFAULT nextval('public.customers_customer_id_seq1'::regclass);


--
-- TOC entry 4863 (class 2604 OID 34008)
-- Name: inserts insert_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inserts ALTER COLUMN insert_id SET DEFAULT nextval('public.inserts_insert_id_seq'::regclass);


--
-- TOC entry 4872 (class 2604 OID 34162)
-- Name: service_logs log_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_logs ALTER COLUMN log_id SET DEFAULT nextval('public.service_logs_log_id_seq'::regclass);


--
-- TOC entry 4866 (class 2604 OID 34127)
-- Name: services service_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.services ALTER COLUMN service_id SET DEFAULT nextval('public.services_service_id_seq'::regclass);


--
-- TOC entry 5067 (class 2606 OID 34147)
-- Name: customer_services customer_services_customer_id_service_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_services
    ADD CONSTRAINT customer_services_customer_id_service_id_key UNIQUE (customer_id, service_id);


--
-- TOC entry 5069 (class 2606 OID 34145)
-- Name: customer_services customer_services_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_services
    ADD CONSTRAINT customer_services_pkey PRIMARY KEY (customer_service_id);


--
-- TOC entry 4993 (class 2606 OID 33685)
-- Name: customers customers_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_email_key UNIQUE (email);


--
-- TOC entry 4995 (class 2606 OID 33683)
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (customer_id);


--
-- TOC entry 5061 (class 2606 OID 34013)
-- Name: inserts inserts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inserts
    ADD CONSTRAINT inserts_pkey PRIMARY KEY (insert_id);


--
-- TOC entry 5084 (class 2606 OID 36008)
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (transaction_id);


--
-- TOC entry 4998 (class 2606 OID 33697)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5001 (class 2606 OID 33714)
-- Name: products_partition_0 products_partition_0_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_0
    ADD CONSTRAINT products_partition_0_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5031 (class 2606 OID 33864)
-- Name: products_partition_10 products_partition_10_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_10
    ADD CONSTRAINT products_partition_10_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5034 (class 2606 OID 33879)
-- Name: products_partition_11 products_partition_11_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_11
    ADD CONSTRAINT products_partition_11_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5037 (class 2606 OID 33894)
-- Name: products_partition_12 products_partition_12_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_12
    ADD CONSTRAINT products_partition_12_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5040 (class 2606 OID 33909)
-- Name: products_partition_13 products_partition_13_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_13
    ADD CONSTRAINT products_partition_13_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5043 (class 2606 OID 33924)
-- Name: products_partition_14 products_partition_14_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_14
    ADD CONSTRAINT products_partition_14_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5046 (class 2606 OID 33939)
-- Name: products_partition_15 products_partition_15_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_15
    ADD CONSTRAINT products_partition_15_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5049 (class 2606 OID 33954)
-- Name: products_partition_16 products_partition_16_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_16
    ADD CONSTRAINT products_partition_16_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5052 (class 2606 OID 33969)
-- Name: products_partition_17 products_partition_17_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_17
    ADD CONSTRAINT products_partition_17_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5055 (class 2606 OID 33984)
-- Name: products_partition_18 products_partition_18_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_18
    ADD CONSTRAINT products_partition_18_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5058 (class 2606 OID 33999)
-- Name: products_partition_19 products_partition_19_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_19
    ADD CONSTRAINT products_partition_19_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5004 (class 2606 OID 33729)
-- Name: products_partition_1 products_partition_1_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_1
    ADD CONSTRAINT products_partition_1_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5007 (class 2606 OID 33744)
-- Name: products_partition_2 products_partition_2_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_2
    ADD CONSTRAINT products_partition_2_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5010 (class 2606 OID 33759)
-- Name: products_partition_3 products_partition_3_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_3
    ADD CONSTRAINT products_partition_3_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5013 (class 2606 OID 33774)
-- Name: products_partition_4 products_partition_4_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_4
    ADD CONSTRAINT products_partition_4_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5016 (class 2606 OID 33789)
-- Name: products_partition_5 products_partition_5_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_5
    ADD CONSTRAINT products_partition_5_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5019 (class 2606 OID 33804)
-- Name: products_partition_6 products_partition_6_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_6
    ADD CONSTRAINT products_partition_6_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5022 (class 2606 OID 33819)
-- Name: products_partition_7 products_partition_7_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_7
    ADD CONSTRAINT products_partition_7_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5025 (class 2606 OID 33834)
-- Name: products_partition_8 products_partition_8_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_8
    ADD CONSTRAINT products_partition_8_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5028 (class 2606 OID 33849)
-- Name: products_partition_9 products_partition_9_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products_partition_9
    ADD CONSTRAINT products_partition_9_pkey PRIMARY KEY (sku, customer_id);


--
-- TOC entry 5076 (class 2606 OID 34168)
-- Name: service_logs service_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_logs
    ADD CONSTRAINT service_logs_pkey PRIMARY KEY (log_id);


--
-- TOC entry 5063 (class 2606 OID 34133)
-- Name: services services_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_pkey PRIMARY KEY (service_id);


--
-- TOC entry 5065 (class 2606 OID 34135)
-- Name: services services_service_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_service_name_key UNIQUE (service_name);


--
-- TOC entry 5070 (class 1259 OID 34246)
-- Name: idx_customer_services_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_customer_services_customer_id ON public.customer_services USING btree (customer_id);


--
-- TOC entry 5071 (class 1259 OID 34247)
-- Name: idx_customer_services_service_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_customer_services_service_id ON public.customer_services USING btree (service_id);


--
-- TOC entry 5059 (class 1259 OID 34122)
-- Name: idx_inserts_sku_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_inserts_sku_customer_id ON public.inserts USING btree (sku, customer_id);


--
-- TOC entry 5077 (class 1259 OID 36018)
-- Name: idx_orders_create_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_create_date ON public.orders USING btree (create_date);


--
-- TOC entry 5078 (class 1259 OID 36015)
-- Name: idx_orders_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_customer_id ON public.orders USING btree (customer_id);


--
-- TOC entry 5079 (class 1259 OID 36016)
-- Name: idx_orders_reference_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_reference_number ON public.orders USING btree (reference_number);


--
-- TOC entry 5080 (class 1259 OID 36019)
-- Name: idx_orders_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_status ON public.orders USING btree (status);


--
-- TOC entry 5081 (class 1259 OID 36017)
-- Name: idx_orders_tracking_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_tracking_number ON public.orders USING btree (tracking_number);


--
-- TOC entry 5082 (class 1259 OID 36014)
-- Name: idx_orders_transaction_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_orders_transaction_id ON public.orders USING btree (transaction_id);


--
-- TOC entry 4996 (class 1259 OID 34101)
-- Name: idx_products_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_products_customer_id ON ONLY public.products USING btree (customer_id);


--
-- TOC entry 5072 (class 1259 OID 34248)
-- Name: idx_service_logs_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_service_logs_customer_id ON public.service_logs USING btree (customer_id);


--
-- TOC entry 5073 (class 1259 OID 34249)
-- Name: idx_service_logs_service_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_service_logs_service_id ON public.service_logs USING btree (service_id);


--
-- TOC entry 5074 (class 1259 OID 34250)
-- Name: idx_service_logs_sku_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_service_logs_sku_customer_id ON public.service_logs USING btree (sku, customer_id);


--
-- TOC entry 4999 (class 1259 OID 34102)
-- Name: products_partition_0_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_0_customer_id_idx ON public.products_partition_0 USING btree (customer_id);


--
-- TOC entry 5029 (class 1259 OID 34112)
-- Name: products_partition_10_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_10_customer_id_idx ON public.products_partition_10 USING btree (customer_id);


--
-- TOC entry 5032 (class 1259 OID 34113)
-- Name: products_partition_11_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_11_customer_id_idx ON public.products_partition_11 USING btree (customer_id);


--
-- TOC entry 5035 (class 1259 OID 34114)
-- Name: products_partition_12_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_12_customer_id_idx ON public.products_partition_12 USING btree (customer_id);


--
-- TOC entry 5038 (class 1259 OID 34115)
-- Name: products_partition_13_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_13_customer_id_idx ON public.products_partition_13 USING btree (customer_id);


--
-- TOC entry 5041 (class 1259 OID 34116)
-- Name: products_partition_14_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_14_customer_id_idx ON public.products_partition_14 USING btree (customer_id);


--
-- TOC entry 5044 (class 1259 OID 34117)
-- Name: products_partition_15_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_15_customer_id_idx ON public.products_partition_15 USING btree (customer_id);


--
-- TOC entry 5047 (class 1259 OID 34118)
-- Name: products_partition_16_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_16_customer_id_idx ON public.products_partition_16 USING btree (customer_id);


--
-- TOC entry 5050 (class 1259 OID 34119)
-- Name: products_partition_17_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_17_customer_id_idx ON public.products_partition_17 USING btree (customer_id);


--
-- TOC entry 5053 (class 1259 OID 34120)
-- Name: products_partition_18_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_18_customer_id_idx ON public.products_partition_18 USING btree (customer_id);


--
-- TOC entry 5056 (class 1259 OID 34121)
-- Name: products_partition_19_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_19_customer_id_idx ON public.products_partition_19 USING btree (customer_id);


--
-- TOC entry 5002 (class 1259 OID 34103)
-- Name: products_partition_1_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_1_customer_id_idx ON public.products_partition_1 USING btree (customer_id);


--
-- TOC entry 5005 (class 1259 OID 34104)
-- Name: products_partition_2_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_2_customer_id_idx ON public.products_partition_2 USING btree (customer_id);


--
-- TOC entry 5008 (class 1259 OID 34105)
-- Name: products_partition_3_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_3_customer_id_idx ON public.products_partition_3 USING btree (customer_id);


--
-- TOC entry 5011 (class 1259 OID 34106)
-- Name: products_partition_4_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_4_customer_id_idx ON public.products_partition_4 USING btree (customer_id);


--
-- TOC entry 5014 (class 1259 OID 34107)
-- Name: products_partition_5_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_5_customer_id_idx ON public.products_partition_5 USING btree (customer_id);


--
-- TOC entry 5017 (class 1259 OID 34108)
-- Name: products_partition_6_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_6_customer_id_idx ON public.products_partition_6 USING btree (customer_id);


--
-- TOC entry 5020 (class 1259 OID 34109)
-- Name: products_partition_7_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_7_customer_id_idx ON public.products_partition_7 USING btree (customer_id);


--
-- TOC entry 5023 (class 1259 OID 34110)
-- Name: products_partition_8_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_8_customer_id_idx ON public.products_partition_8 USING btree (customer_id);


--
-- TOC entry 5026 (class 1259 OID 34111)
-- Name: products_partition_9_customer_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX products_partition_9_customer_id_idx ON public.products_partition_9 USING btree (customer_id);


--
-- TOC entry 5085 (class 0 OID 0)
-- Name: products_partition_0_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_0_customer_id_idx;


--
-- TOC entry 5086 (class 0 OID 0)
-- Name: products_partition_0_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_0_pkey;


--
-- TOC entry 5105 (class 0 OID 0)
-- Name: products_partition_10_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_10_customer_id_idx;


--
-- TOC entry 5106 (class 0 OID 0)
-- Name: products_partition_10_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_10_pkey;


--
-- TOC entry 5107 (class 0 OID 0)
-- Name: products_partition_11_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_11_customer_id_idx;


--
-- TOC entry 5108 (class 0 OID 0)
-- Name: products_partition_11_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_11_pkey;


--
-- TOC entry 5109 (class 0 OID 0)
-- Name: products_partition_12_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_12_customer_id_idx;


--
-- TOC entry 5110 (class 0 OID 0)
-- Name: products_partition_12_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_12_pkey;


--
-- TOC entry 5111 (class 0 OID 0)
-- Name: products_partition_13_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_13_customer_id_idx;


--
-- TOC entry 5112 (class 0 OID 0)
-- Name: products_partition_13_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_13_pkey;


--
-- TOC entry 5113 (class 0 OID 0)
-- Name: products_partition_14_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_14_customer_id_idx;


--
-- TOC entry 5114 (class 0 OID 0)
-- Name: products_partition_14_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_14_pkey;


--
-- TOC entry 5115 (class 0 OID 0)
-- Name: products_partition_15_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_15_customer_id_idx;


--
-- TOC entry 5116 (class 0 OID 0)
-- Name: products_partition_15_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_15_pkey;


--
-- TOC entry 5117 (class 0 OID 0)
-- Name: products_partition_16_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_16_customer_id_idx;


--
-- TOC entry 5118 (class 0 OID 0)
-- Name: products_partition_16_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_16_pkey;


--
-- TOC entry 5119 (class 0 OID 0)
-- Name: products_partition_17_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_17_customer_id_idx;


--
-- TOC entry 5120 (class 0 OID 0)
-- Name: products_partition_17_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_17_pkey;


--
-- TOC entry 5121 (class 0 OID 0)
-- Name: products_partition_18_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_18_customer_id_idx;


--
-- TOC entry 5122 (class 0 OID 0)
-- Name: products_partition_18_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_18_pkey;


--
-- TOC entry 5123 (class 0 OID 0)
-- Name: products_partition_19_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_19_customer_id_idx;


--
-- TOC entry 5124 (class 0 OID 0)
-- Name: products_partition_19_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_19_pkey;


--
-- TOC entry 5087 (class 0 OID 0)
-- Name: products_partition_1_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_1_customer_id_idx;


--
-- TOC entry 5088 (class 0 OID 0)
-- Name: products_partition_1_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_1_pkey;


--
-- TOC entry 5089 (class 0 OID 0)
-- Name: products_partition_2_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_2_customer_id_idx;


--
-- TOC entry 5090 (class 0 OID 0)
-- Name: products_partition_2_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_2_pkey;


--
-- TOC entry 5091 (class 0 OID 0)
-- Name: products_partition_3_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_3_customer_id_idx;


--
-- TOC entry 5092 (class 0 OID 0)
-- Name: products_partition_3_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_3_pkey;


--
-- TOC entry 5093 (class 0 OID 0)
-- Name: products_partition_4_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_4_customer_id_idx;


--
-- TOC entry 5094 (class 0 OID 0)
-- Name: products_partition_4_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_4_pkey;


--
-- TOC entry 5095 (class 0 OID 0)
-- Name: products_partition_5_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_5_customer_id_idx;


--
-- TOC entry 5096 (class 0 OID 0)
-- Name: products_partition_5_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_5_pkey;


--
-- TOC entry 5097 (class 0 OID 0)
-- Name: products_partition_6_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_6_customer_id_idx;


--
-- TOC entry 5098 (class 0 OID 0)
-- Name: products_partition_6_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_6_pkey;


--
-- TOC entry 5099 (class 0 OID 0)
-- Name: products_partition_7_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_7_customer_id_idx;


--
-- TOC entry 5100 (class 0 OID 0)
-- Name: products_partition_7_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_7_pkey;


--
-- TOC entry 5101 (class 0 OID 0)
-- Name: products_partition_8_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_8_customer_id_idx;


--
-- TOC entry 5102 (class 0 OID 0)
-- Name: products_partition_8_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_8_pkey;


--
-- TOC entry 5103 (class 0 OID 0)
-- Name: products_partition_9_customer_id_idx; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.idx_products_customer_id ATTACH PARTITION public.products_partition_9_customer_id_idx;


--
-- TOC entry 5104 (class 0 OID 0)
-- Name: products_partition_9_pkey; Type: INDEX ATTACH; Schema: public; Owner: postgres
--

ALTER INDEX public.products_pkey ATTACH PARTITION public.products_partition_9_pkey;


--
-- TOC entry 5133 (class 2620 OID 36021)
-- Name: orders update_orders_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON public.orders FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 5127 (class 2606 OID 34148)
-- Name: customer_services customer_services_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_services
    ADD CONSTRAINT customer_services_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(customer_id) ON DELETE CASCADE;


--
-- TOC entry 5128 (class 2606 OID 34153)
-- Name: customer_services customer_services_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_services
    ADD CONSTRAINT customer_services_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(service_id) ON DELETE CASCADE;


--
-- TOC entry 5126 (class 2606 OID 34014)
-- Name: inserts inserts_sku_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inserts
    ADD CONSTRAINT inserts_sku_customer_id_fkey FOREIGN KEY (sku, customer_id) REFERENCES public.products(sku, customer_id) ON DELETE CASCADE;


--
-- TOC entry 5132 (class 2606 OID 36009)
-- Name: orders orders_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(customer_id) ON DELETE CASCADE;


--
-- TOC entry 5125 (class 2606 OID 33698)
-- Name: products products_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE public.products
    ADD CONSTRAINT products_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(customer_id) ON DELETE CASCADE;


--
-- TOC entry 5129 (class 2606 OID 34169)
-- Name: service_logs service_logs_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_logs
    ADD CONSTRAINT service_logs_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(customer_id) ON DELETE CASCADE;


--
-- TOC entry 5130 (class 2606 OID 34174)
-- Name: service_logs service_logs_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_logs
    ADD CONSTRAINT service_logs_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(service_id) ON DELETE CASCADE;


--
-- TOC entry 5131 (class 2606 OID 34179)
-- Name: service_logs service_logs_sku_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.service_logs
    ADD CONSTRAINT service_logs_sku_customer_id_fkey FOREIGN KEY (sku, customer_id) REFERENCES public.products(sku, customer_id) ON DELETE CASCADE;


--
-- TOC entry 5282 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


-- Completed on 2024-06-04 22:50:52

--
-- PostgreSQL database dump complete
--

