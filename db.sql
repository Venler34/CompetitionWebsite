CREATE TABLE public."Users" (
    id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    score double precision DEFAULT '0'::double precision,
    name text NOT NULL,
    password bigint NOT NULL
);