--
-- PostgreSQL database dump
--

\restrict xLrqhcFfF8p1VlZXRrIak0K9ilTGCkKP0miMVqZyx9I5or3YxWK76KY2v7u56iP

-- Dumped from database version 17.11 (Debian 17.11-1.pgdg13+2)
-- Dumped by pg_dump version 17.11 (Debian 17.11-1.pgdg13+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- Name: pannes; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.pannes (
    id integer NOT NULL,
    nb_clients_impactes character varying(255),
    date_debut timestamp without time zone,
    date_fin timestamp without time zone,
    pannep text,
    longitude double precision,
    latitude double precision,
    statut character varying(255),
    info_non_utilise character varying(255),
    cause character varying(255),
    id_municipalite character varying(255),
    id_msg_panne text,
    callid_processed bigint
);


ALTER TABLE public.pannes OWNER TO root;

--
-- Name: pannes_id_seq; Type: SEQUENCE; Schema: public; Owner: root
--

ALTER TABLE public.pannes ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.pannes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: processed_ids; Type: TABLE; Schema: public; Owner: root
--

CREATE TABLE public.processed_ids (
    id bigint NOT NULL,
    created timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.processed_ids OWNER TO root;

--
-- Name: pannes pannes_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.pannes
    ADD CONSTRAINT pannes_pkey PRIMARY KEY (id);


--
-- Name: processed_ids processed_ids_pkey; Type: CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.processed_ids
    ADD CONSTRAINT processed_ids_pkey PRIMARY KEY (id);


--
-- Name: pannes fk_callid_processed; Type: FK CONSTRAINT; Schema: public; Owner: root
--

ALTER TABLE ONLY public.pannes
    ADD CONSTRAINT fk_callid_processed FOREIGN KEY (callid_processed) REFERENCES public.processed_ids(id);


--
-- PostgreSQL database dump complete
--

\unrestrict xLrqhcFfF8p1VlZXRrIak0K9ilTGCkKP0miMVqZyx9I5or3YxWK76KY2v7u56iP

