-- WARNING: this query may be part of multiple repos
-- part of a query repo
-- query name: EVM wallet_addresses
-- query link: https://dune.com/queries/4202269


WITH all_transaction AS (
  SELECT
    "from" AS address,
    block_time
  FROM ethereum.transactions
  UNION ALL
  SELECT
    "to" AS address,
    block_time
  FROM ethereum.transactions
  WHERE "to" NOT IN (SELECT address FROM ethereum.contracts)
  AND "from" NOT IN (SELECT address FROM ethereum.contracts)
)
SELECT
  ROW_NUMBER() OVER (ORDER BY MIN(block_time)) AS No,
  address AS wallet_address,
  MIN(block_time) AS create_time
FROM all_transaction
WHERE address IS NOT NULL
GROUP BY address
OFFSET 2100000
LIMIT 1000000